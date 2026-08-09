[Home](../README.md) > Seals and Interpropellant Seals

# Seals and Interpropellant Seals

## Contents

- [Overview](#overview)
- [The interpropellant seal](#the-interpropellant-seal)
- [Seal types](#seal-types)
- [Purge](#purge)
- [Seals drive rotordynamics](#seals-drive-rotordynamics)
- [Leakage is a design quantity](#leakage-is-a-design-quantity)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The seal package on a turbopump does three jobs that have nothing to do with each other: it keeps propellant inside the machine, it keeps oxidiser away from fuel, and it substantially decides whether the rotor is stable.

The second of those is the one with no acceptable failure mode.

---

## The interpropellant seal

On a common shaft turbopump the fuel pump and the oxidiser pump are on the same shaft with the turbine between or beside them. **A leak path between them is a mixed propellant leak inside a spinning machine.**

For a hypergolic combination that is an ignition. For LOX and a hydrocarbon it is a fire waiting for an ignition source, and a rotating shaft in a bearing is an ignition source.

**The standard arrangement is not one seal but a sequence:** a seal on the oxidiser side, a drained and vented cavity, an inert purge, another drained cavity, and a seal on the fuel side. Anything that leaks past the first seal is caught, diluted and vented overboard before it can reach anything that leaks past the second.

**The vent has to go overboard and it has to keep working**, which makes it a plumbing item on the outside of the engine that people forget is safety critical. A blocked interpropellant drain converts a designed-for leak into a mixing chamber.

**Separate shafts remove the problem entirely**, which is one of several reasons RS-25 has separate high pressure fuel and oxidiser turbopumps rather than one machine. It costs a second turbine and a second set of bearings.

---

## Seal types

| Type | Character |
|---|---|
| Labyrinth | Non-contacting, tolerant, leaks by design. The workhorse |
| Floating ring | Closer clearance, better leakage, and it moves with the rotor |
| Face seal | Contacting, low leakage, and it wears |
| Lift-off face seal | Contacts at rest and lifts on a gas film in operation |
| Damper seal | A labyrinth designed for rotordynamic damping rather than for leakage |

**A labyrinth seal does not seal.** It is a controlled leakage path that dissipates pressure across a series of throttling steps, and its leakage is a design quantity rather than a defect. Treating it as a sealing element is a common misreading and it leads to leakage budgets that do not close.

**Face seals wear**, so they are life-limited items on a reusable engine and single-use items on an expendable one. A lift-off design contacts only at rest and start, which removes most of the wear at the cost of a start transient during which it is neither sealing nor lifted.

---

## Purge

Inert gas, usually helium or nitrogen, injected into the cavities between seals.

It does three things. It **dilutes** whatever leaks past a seal below anything that can react. It **pressurises** the cavity so leakage flows outward into the vent rather than inward into the next cavity. And it **excludes** atmosphere, which matters for a cryogenic seal that would otherwise freeze condensed water and ice a clearance shut.

**Purge is required before start and after shutdown as well as during operation**, and the after-shutdown case is the one that gets missed. A hot machine soaking back with residual propellant in it and no purge is exactly the condition the seal package exists to prevent. See the same soakback reasoning in [thermalManagement](../../../thermalManagement/docs/ThermalModelling.md).

Purge consumption is a real vehicle-level quantity: it needs a bottle, a regulator and a schedule, and it is owned by [fluidSystems](../../../fluidSystems/README.md).

---

## Seals drive rotordynamics

The point most easily missed, and it is why this document sits next to [ShaftDynamics](ShaftDynamics.md) rather than in a fluids section.

A fluid film in a narrow annulus around a rotating shaft develops a **cross-coupled stiffness**: displace the rotor radially and the film pushes it tangentially rather than back. That tangential force is what drives subsynchronous whirl, and the seals are usually the largest contributor to it in a turbopump.

**So a seal chosen purely for leakage can destabilise the rotor.** Damper seals and swirl brakes exist to reverse the effect: they are seals designed for their rotordynamic coefficients, and their leakage is a secondary consideration.

That inverts the usual design order. On a machine that has had a whirl problem, the seals are a rotordynamic component that happens to leak.

---

## Leakage is a design quantity

It has to be budgeted, not minimised.

**Overboard leakage** is propellant lost, and it appears in the mass budget.

**Interpropellant leakage** is caught by the purge and vent arrangement, and its magnitude sizes that arrangement.

**Turbine-side leakage** on a closed cycle goes somewhere that matters thermodynamically, so it appears in the cycle balance rather than only in the mass budget.

A leakage budget that assumes a labyrinth seals is a budget that will not close, and the discovery usually happens on a test stand.

---

## Design rules of thumb

- **Sequence the interpropellant seal.** Seal, drain, purge, drain, seal, and vent overboard.
- **Treat the interpropellant drain as safety critical.** A blocked one makes a mixing chamber.
- **Consider separate shafts** if the interpropellant risk dominates. It costs a turbine and removes the problem.
- **Budget labyrinth leakage rather than assuming it seals.**
- **Purge before start and after shutdown**, not only during operation.
- **Choose seals for rotordynamic coefficients if whirl is a risk**, and accept the leakage that comes with it.
- **Life-limit contacting seals explicitly** on a reusable machine.

---

## Failure modes

**Interpropellant leak.** Fire or detonation inside a spinning machine. No acceptable version of this exists.

**Blocked interpropellant drain.** Converts a designed-for leak into a mixing chamber, and nothing upstream shows it.

**Purge omitted after shutdown.** Soakback with residual propellant and no dilution.

**A labyrinth assumed to seal.** The leakage budget does not close and the discovery is on the stand.

**Seals selected on leakage alone.** Cross-coupled stiffness destabilises the rotor.

**Face seal life not tracked on a reusable engine.** It is a wear item and it is inside the machine.

**Cryogenic seal iced by ambient moisture.** Purge excludes atmosphere and its absence lets a clearance freeze shut.

---

## Standards

| Standard | What it gives you |
|---|---|
| **NASA SP-8121** | **Liquid rocket engine turbopump rotating shaft seals.** The design monograph |
| NASA SP-8048 | Turbopump bearings, which share the cavity |
| NASA SP-8107 | Turbopump systems |
| ASTM G93 | Cleaning for oxygen service, which the oxidiser side seal package needs |
| NASA-STD-6001 | Materials compatibility, including oxygen compatibility |

---

## Tool interface

There is no seal class in this library. Seal leakage and seal materials are covered by [fluidSystems](../../../fluidSystems/fluidSystemsLibrary/docs/Seals.md), which owns the seal material table and the leakage machinery, and duplicating either here would create a second definition of the same thing.

What this sub-domain contributes is the requirement: a shaft speed, a pressure differential and a propellant pair.

---

## References

- NASA SP-8121, *Liquid rocket engine turbopump rotating shaft seals*
- Childs, *Turbomachinery Rotordynamics*, the seal coefficient chapters
- NASA SP-8107, *Turbopump systems for liquid rocket engines*
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
