[Home](../README.md) > Shaft Dynamics

# Shaft Dynamics

## Contents

- [Overview](#overview)
- [Why there is no class for this](#why-there-is-no-class-for-this)
- [Critical speeds](#critical-speeds)
- [Subsynchronous whirl](#subsynchronous-whirl)
- [Bearings](#bearings)
- [Axial thrust balance](#axial-thrust-balance)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A turbopump shaft carries a pump impeller at one end, a turbine at the other, and runs somewhere between twenty and a hundred thousand revolutions per minute in bearings cooled by the propellant they are immersed in.

Rotordynamics is where turbopump programmes lose time. The hydraulic design is tractable, the thermal design is tractable, and the shaft is where a machine that works on paper turns out to be unbuildable.

---

## Why there is no class for this

The sub-domain scaffold planned a `ShaftSystem` class and it was not built, deliberately.

Two of the things it was meant to carry turned out to belong elsewhere. **The bearing DN limit lives in `Pump.sizeImpeller`**, because it follows from the impeller diameter and there is no sense computing it apart from the geometry that sets it. **The cavitation ceiling on shaft speed lives in `Inducer.maximumShaftSpeed`**, for the same reason.

What was left is critical speed and bearing life, and both need inputs this repository does not have.

**A critical speed needs the shaft stiffness and the bearing support stiffness.** Both depend on a detailed layout that does not exist at the stage this library operates. A class that computed a critical speed from an assumed stiffness would be inventing the input that decides the answer, and reporting it to three figures.

**Bearing life needs manufacturer load ratings.** They are published per part number and this repository does not carry a bearing catalogue.

So this document exists and the class does not. That is the same reasoning that left three [aerospaceMaterials](../../../aerospaceMaterials/README.md) sub-domains documentation-only, and it is recorded here rather than left as an absence.

---

## Critical speeds

A shaft has natural bending frequencies. Running at one of them is a resonance with very little to damp it.

**Subcritical operation** runs below the first critical speed. It is the simple choice and it demands a stiff, short shaft, which conflicts with fitting a pump, a turbine and a seal package on it.

**Supercritical operation** runs between the first and second criticals, accepting that the machine passes through a resonance during start and shutdown. This is normal on high speed turbopumps, and it is why start and shutdown transients are a rotordynamics problem as well as a thermal one. The machine spends a fraction of a second in resonance and the damping has to be adequate for that fraction of a second.

The usual requirement is a margin of **20 per cent** between operating speed and any critical, in whichever direction.

**A stiffer bearing raises the critical speed and transmits more load to the housing.** That trade is the heart of the layout problem and it cannot be resolved from a specific speed.

---

## Subsynchronous whirl

The failure mode that ends programmes rather than delaying them.

The rotor orbits its own axis at a frequency below the shaft speed, driven by fluid forces in the seals and the impeller passages rather than by imbalance. It is self-excited, so it does not respond to balancing, and once it starts it grows.

**It is a stability problem, not a response problem.** There is no margin on it any more than there is on combustion instability, which is the same category of failure in a different physical system: a coupling that either grows or decays, decided by a design detail.

The seals are the usual culprit, because a fluid film in a narrow annulus develops a cross-coupled stiffness that pushes the rotor tangentially. **Damper seals and swirl brakes exist to fix exactly this** and they are fitted on machines that have had the problem rather than on machines that might.

---

## Bearings

Rolling element bearings, cooled and lubricated by the propellant, which for LOX means a bearing running dry of anything conventional.

**The DN number** is bore diameter in millimetres times shaft speed in rpm, and it is the classical limit. Two million is a reasonable ceiling for a propellant-cooled bearing.

The worked example runs at **1.12 million**, which is comfortable and is not the binding constraint. It becomes binding on a large pump, where the bore diameter grows with the impeller.

**A LOX bearing has no lubricant.** Anything organic is a fire hazard in liquid oxygen, so the bearing runs on a transferred film from a solid lubricant cage and its life is short by any industrial standard. That is one of several reasons hydrostatic bearings appear on reusable engines: no rolling elements, no wear mechanism, and a life limited by something other than contact fatigue.

---

## Axial thrust balance

The impeller has high pressure on one face and low on the other, so it generates a large axial force. The turbine generates another. They do not cancel.

**The residual has to be carried by a thrust bearing or balanced hydraulically**, and hydraulically is usually the answer above a certain size because the residual force can exceed what a bearing will take for the required life.

A balance piston is a controlled leakage path that develops a restoring force: if the rotor moves one way, the clearance changes, the pressure changes, and it pushes back. It works well and it couples the axial and rotordynamic behaviour, which is one more thing that has to be analysed together rather than separately.

---

## Design rules of thumb

- **Keep 20 per cent margin from any critical speed**, in whichever direction.
- **Expect supercritical operation on a fast machine**, and analyse the transient through the resonance.
- **Treat subsynchronous whirl as a stability question**, not a margin.
- **Fit damper seals or swirl brakes if whirl appears.** Balancing will not help.
- **Keep DN below two million** for a propellant-cooled rolling element bearing.
- **Balance the axial thrust hydraulically above a modest size**, and analyse the balance piston with the rotordynamics rather than apart from it.
- **Assume a LOX bearing has no lubricant** and size its life accordingly.

---

## Failure modes

**Subsynchronous whirl.** Self-excited, grows, does not respond to balancing, and ends programmes.

**A critical speed inside the operating range.** Very little damps it.

**A transient that dwells near a critical.** Supercritical operation is fine if the machine passes through quickly and not if it lingers.

**Thrust balance analysed apart from the rotordynamics.** The balance piston couples them.

**Bearing life estimated from an industrial catalogue value.** A propellant-cooled bearing with no conventional lubricant is a different machine.

**DN checked at the pump and not at the turbine end.** They can differ.

---

## Worked numbers

The worked example turbopump.

| Quantity | Value |
|---|---|
| Shaft speed | 30 000 rpm |
| Impeller diameter | 106.6 mm |
| Assumed bearing bore | 37 mm |
| DN number | 1.12 million against a 2.0 million limit |
| Critical speed margin required | 20 % |

**No critical speed is computed here, and that is deliberate.** See [why there is no class for this](#why-there-is-no-class-for-this).

---

## Standards

| Standard | What it gives you |
|---|---|
| **NASA SP-8048** | **Liquid rocket engine turbopump bearings.** The design monograph |
| NASA SP-8107 | Turbopump systems |
| API 684 | Rotordynamics tutorial, industrial but the machinery is general |
| ISO 1940 | Balance quality grades |
| NASA-STD-5012 | Strength and life assessment for rocket engines |

---

## Tool interface

The DN check is on the pump, because it follows from the impeller diameter.

```python
from Pump import Pump

pump = Pump()
pump.setInputs({'propellant': 'RP-1', 'density': 810.0, 'massFlow': 10.34,
                'pressureRise': 12.5e6, 'shaftSpeed': 30000.0})

impeller = pump.sizeImpeller()

print(impeller['dnNumber'], impeller['dnWithinLimit'])
```

There is no critical speed method, and there will not be one until the library carries a shaft layout.

---

## References

- NASA SP-8048, *Liquid rocket engine turbopump bearings*
- NASA SP-8107, *Turbopump systems for liquid rocket engines*
- Childs, *Turbomachinery Rotordynamics*
- Vance, *Rotordynamics of Turbomachinery*
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
