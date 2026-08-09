[Home](../README.md) > Propulsion Overview

# Propulsion Overview

## Contents

- [Overview](#overview)
- [The one factorisation everything rests on](#the-one-factorisation-everything-rests-on)
- [The order decisions get made in](#the-order-decisions-get-made-in)
- [What sizes an engine](#what-sizes-an-engine)
- [The design rules of thumb](#the-design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Where this domain stops](#where-this-domain-stops)
- [Where the domain sits](#where-the-domain-sits)
- [Tool interface](#tool-interface)
- [Documents in this domain](#documents-in-this-domain)
- [Sub-domains](#sub-domains)
- [References](#references)

---

## Overview

This domain is the engine: everything between the tank outlet and the nozzle exit, for liquid bipropellant engines specifically. Pump-fed and pressure-fed, storable and cryogenic, from a small upper stage engine to a booster.

Monopropellant hydrazine, catalyst beds and the feed system upstream of the engine inlet live in [fluidSystems](../../fluidSystems/README.md) and are not repeated here.

The documents at this level cover the engine as a system: what the performance parameters mean, how they relate, what the propellant choice buys, and what actually sets the size of the hardware. The [sub-domains](#sub-domains) cover the hardware itself.

---

## The one factorisation everything rests on

```
F = Cf c* mdot
```

Thrust is a thrust coefficient times a characteristic velocity times a mass flow. The factorisation is not an algebraic convenience. It is a partition of the engine into two halves that cannot affect each other.

| Parameter | Contains | Measured by |
|---|---|---|
| `c*` | Injector, chamber, mixing, residence time, combustion | `Pc At / mdot`, no thrust measurement needed |
| `Cf` | Area ratio, contour, divergence, ambient pressure | Thrust, once `c*` is known |

**Nothing the nozzle does can change `c*`, and nothing the injector does can change `Cf`.**

That is what makes the split a diagnostic rather than a bookkeeping choice. An engine five per cent down on specific impulse tells you only that something is wrong. The same engine measured at nominal `c*` tells you the problem is downstream of the throat, and no amount of injector work will find it.

The corollary is that a combined efficiency is nearly useless on its own. **94 per cent overall is 96 times 98, and it is also 98 times 96**, and those are different engines with different fixes. The [EnginePerformance](PerformanceFundamentals.md) class carries the two separately and refuses to collapse them for this reason.

---

## The order decisions get made in

Propulsion decisions are strongly ordered, and taking them out of order produces work that has to be redone.

**The cycle first.** Gas generator, staged combustion, expander or pressure-fed. It sets the achievable chamber pressure, the turbomachinery, the plumbing and a large part of the mass, and everything after it is conditioned on it. See [engineCycles](../engineCycles/README.md).

**Then the propellant.** Constrained by the cycle, by storability requirements and by the stage. It is chosen on density impulse for a booster and closer to specific impulse for an upper stage, and those rank the candidates differently. See [PropellantSelection](PropellantSelection.md).

**Then the chamber pressure.** Higher is better for performance and worse for everything else: the feed system, the cooling, the structure and the turbomachinery all get harder together.

**Then the expansion.** Set by where the engine operates, bounded above by flow separation at the lowest ambient pressure it must run at. This is the decision the [worked example](../codeInterface.py) is built around, because it has three defensible answers that disagree.

**Then the geometry**, which by that point is mostly forced.

---

## What sizes an engine

Two answers, and which is right depends on the chamber pressure.

**Characteristic length** sets a chamber volume from the residence time combustion needs, `Vc = L* At`. It says nothing about the shape of that volume.

**Cooling** sets a wall area from the heat load, and wall area and volume are different functions of the geometry.

The two swap over. For a 100 kN LOX/RP-1 engine at an area ratio of 20:

| Chamber pressure | Cooling margin | Governed by |
|---|---|---|
| 5 MPa | 3.78 | Characteristic length |
| 10 MPa | 1.62 | Characteristic length |
| 16 MPa | 1.01 | Characteristic length, barely |
| 18 MPa | 0.91 | Cooling |
| 30 MPa | 0.58 | Cooling |

**Below roughly 16 MPa combustion sizes the chamber and above it cooling does.** That is the reason high chamber pressure engines look different: they are longer than their residence time requires, and the extra length is wall area.

The cross-check has to count the whole gas-side wall. On the worked example the divergent section is 66 per cent of the wetted area, and a cooling check run on the barrel alone reaches the opposite conclusion.

**Residence time is independent of both chamber pressure and engine size.** Substituting `At = mdot c* / Pc` and the chamber gas density into `t = Vc rho / mdot` gives

```
t = L* c* / (R Tc)
```

and both `Pc` and `mdot` cancel. A 10 kN engine and a 1000 kN engine on the same propellant at the same `L*` hold their propellant for the same 1.47 milliseconds. That is worth knowing before scaling an engine and expecting the combustion to behave differently.

---

## The design rules of thumb

- **Diagnose with `c*` before touching anything.** It separates the combustion problem from the nozzle problem and it needs no thrust measurement.
- **Choose the propellant on density impulse for a booster** and closer to specific impulse for an upper stage. The two orderings disagree.
- **Size the expansion for where the engine operates**, not for the condition the thrust requirement is written at.
- **Stop short of the separation limit**, and hold margin off it. Summerfield is a correlation with real scatter.
- **Expect cooling to govern the chamber above roughly 16 MPa** and combustion to govern below it, and check rather than assume.
- **Count the nozzle in any wall area calculation.** It is usually the majority of it.
- **State the ambient pressure a thrust is quoted at.** A 100 kN sea level engine and a 100 kN vacuum engine are different engines.

---

## Failure modes

**Diagnosing an Isp shortfall without measuring `c*`.** The two halves have nothing in common and the combined number does not distinguish them.

**Sizing the expansion at the thrust requirement condition.** A first stage requirement is written at sea level and the engine spends almost none of its burn there. The [worked example](../codeInterface.py) costs 61 m/s of stage delta-V this way.

**Designing on the separation limit rather than short of it.** The criterion has scatter and the failure past it is a side load rather than a performance penalty.

**Throttling a sea level engine that was expanded to the separation limit.** Exit pressure falls with chamber pressure, so the nozzle separates as soon as it throttles. See [ThrottlingAndMixtureRatio](ThrottlingAndMixtureRatio.md).

**Checking cooling on the barrel alone.** Understates the available wall area by a factor of three on a moderately expanded engine.

**Assuming a bigger engine has more residence time.** It does not. Residence time is a propellant and `L*` property.

---

## Where this domain stops

**Nozzle contour generation lives in the NOVA suite**, which generates method of characteristics contours and cooling channel geometry and exports CAD-ready output.

This domain covers nozzle performance, area ratio selection, thrust coefficient and the altitude compensation trades: the decisions, not the geometry generation. The [nozzles](../nozzles/README.md) sub-domain says so explicitly.

That division is deliberate. Reimplementing a contour generator here would create a second implementation with nothing enforcing agreement between them, which is the same argument that keeps `joiningProcesses` in [aerospaceMaterials](../../aerospaceMaterials/README.md) documentation-only against `Weld.py`.

---

## Where the domain sits

| Domain | What crosses the boundary |
|---|---|
| [fluidSystems](../../fluidSystems/README.md) | Everything upstream of the engine inlet, and the monopropellant case |
| [thermalManagement](../../thermalManagement/README.md) | Regenerative cooling is a heat exchanger, and the nozzle radiates |
| [aerospaceStructures](../../aerospaceStructures/README.md) | Thrust structure, gimbal loads, chamber as a pressure vessel |
| [aerospaceMaterials](../../aerospaceMaterials/README.md) | Copper alloy liners, superalloy turbine hardware, additive manufacture |
| [environmentsAndLoads](../../environmentsAndLoads/README.md) | The engine is the dominant source of vibration and acoustics |
| [vehicleArchitecture](../../vehicleArchitecture/README.md) | Engine performance and mass are the inputs to vehicle sizing |

**The coupling worth naming is that the fuel flow is simultaneously the coolant supply.** On the worked example, 10.34 kg/s of RP-1 both feeds the injector and carries a 2.72 MW wall load. The cooling circuit and the feed system are one problem owned by two directories.

---

## Tool interface

```python
from PropellantCombination import PropellantCombination
from EnginePerformance import EnginePerformance
from EngineSizing import EngineSizing

combination = PropellantCombination()
combination.setInputs({'combination': 'LOX/RP-1', 'areaRatio': 40.0})
print(combination.calculateDensityImpulse()['densityImpulse'])

performance = EnginePerformance()
performance.setInputs({'combination': 'LOX/RP-1', 'chamberPressure': 10.0e6,
                       'areaRatio': 20.35})
print(performance.calculateSpecificImpulse()['delivered'])

sizing = EngineSizing()
sizing.setInputs({'combination': 'LOX/RP-1', 'thrust': 100000.0,
                  'chamberPressure': 10.0e6, 'areaRatio': 20.35})
print(sizing.sizeChamber()['governing'])
```

| Class | Answers |
|---|---|
| [PropellantCombination](PropellantSelection.md) | Which propellant, and on which figure of merit |
| [EnginePerformance](PerformanceFundamentals.md) | What impulse, at what altitude, and which half is losing it |
| [EngineSizing](EngineSizing.md) | What geometry, and what governed it |

---

## Documents in this domain

| Document | Covers |
|---|---|
| [PerformanceFundamentals.md](PerformanceFundamentals.md) | Isp, c*, Cf, the efficiencies, altitude behaviour, separation |
| [PropellantSelection.md](PropellantSelection.md) | Combinations, density impulse, storability, the volume split |
| [EngineSizing.md](EngineSizing.md) | Thrust to throat to chamber to mass, and what governs each |
| [ThrottlingAndMixtureRatio.md](ThrottlingAndMixtureRatio.md) | Injector authority, the throttle floor, propellant utilisation |
| [EngineIntegration.md](EngineIntegration.md) | Gimbal, plumbing, heat soak, the interfaces either side |
| [StandardsIndex.md](StandardsIndex.md) | The standards, and what each is actually for |

---

## Sub-domains

| Sub-domain | Covers |
|---|---|
| [combustionDevices](../combustionDevices/README.md) | Injectors, chamber sizing, combustion stability, regenerative cooling |
| [turbomachinery](../turbomachinery/README.md) | Pumps, turbines, inducers, cavitation, shaft dynamics |
| [engineCycles](../engineCycles/README.md) | Gas generator, staged combustion, expander, pressure-fed, power balance |
| [nozzles](../nozzles/README.md) | Performance, area ratio, thrust coefficient, altitude compensation |
| [ignitionAndStart](../ignitionAndStart/README.md) | Igniters, start and shutdown transients, chill-in, purge |
| [propulsionTesting](../propulsionTesting/README.md) | Hot fire campaigns, test stands, instrumentation, data reduction |

---

## References

- Sutton and Biblarz, *Rocket Propulsion Elements*
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
- NASA SP-125, *Design of Liquid Propellant Rocket Engines*
- Gordon and McBride, *Computer Program for Calculation of Complex Chemical Equilibrium Compositions*, the CEA reference
- Barrere et al., *Rocket Propulsion*
