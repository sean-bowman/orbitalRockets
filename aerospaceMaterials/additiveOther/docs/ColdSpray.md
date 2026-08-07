[Home](../README.md) > Cold Spray

# Cold Spray

## Contents

- [Overview](#overview)
- [The mechanism](#the-mechanism)
- [Critical velocity](#critical-velocity)
- [What it achieves](#what-it-achieves)
- [Where it wins](#where-it-wins)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Powder is accelerated to supersonic velocity in a heated gas jet and impacts a substrate, where it deforms plastically and bonds in the solid state. Nothing melts. That single fact is what the process is for.

---

## The mechanism

| Step | Detail |
|---|---|
| **1. Acceleration** | Gas through a de Laval nozzle to 500 to 1200 m/s |
| **2. Impact** | The particle strikes the substrate |
| **3. Adiabatic shear instability** | The deformation is so fast the heat cannot conduct away |
| **4. Oxide disruption** | The surface oxide fractures and is extruded outward |
| **5. Bonding** | Clean metal meets clean metal under enormous pressure |

**The bond is metallurgical and mechanical together.** Adiabatic shear at the interface disrupts the oxide films on both particle and substrate, exposing clean metal at a pressure of several gigapascals, and it bonds.

**Gas temperature is well below the melting point.** It is heated to accelerate it, and the particle spends microseconds in the jet, so it does not melt. Helium gives higher velocities than nitrogen at the same temperature and it is much more expensive.

---

## Critical velocity

**Below a material-specific critical velocity, particles do not bond. They erode the substrate instead.**

| Material | Critical velocity |
|---|---|
| **Aluminium** | 620 to 700 m/s |
| Copper | 550 to 580 m/s |
| Nickel | 620 to 650 m/s |
| **Titanium** | **700 to 890 m/s** |
| Stainless steel | 700 to 900 m/s |

**There is also an upper limit**, above which the particle erodes rather than bonds. The usable window is roughly 1.0 to 1.5 times the critical velocity, and staying in it is the process control problem.

**Softer, denser materials bond more easily**, which is why copper and aluminium cold spray is mature and titanium is harder. Titanium's high critical velocity requires helium or very high gas temperatures.

**Particle size matters** because smaller particles accelerate more readily and decelerate more in the bow shock at the substrate. There is an optimum size range, typically 10 to 50 micrometres, and out-of-spec powder simply does not bond.

---

## What it achieves

| Property | Value |
|---|---|
| **Rate** | **500 to 3000 cm^3/h.** Very high |
| Tolerance | IT13 |
| Surface | Rough |
| **Size** | **Unlimited.** The gun is handheld or robot mounted |
| **Porosity** | 1 to 5 %, and lower with heat treatment |
| **Properties** | **Heavily cold worked.** High strength, low ductility |
| **Substrate HAZ** | **None** |

**The deposit is heavily cold worked** because every particle arrived by severe plastic deformation. That gives high strength and hardness and very low ductility, and a post-deposition anneal is usual where ductility matters.

**No HAZ in the substrate at all** is the property that has no equivalent in any fusion process, and it is the entire argument for cold spray in repair.

**Adhesion is the limiting property**, not cohesion. The deposit-to-substrate bond is generally weaker than the deposit itself, and it is the design allowable. Substrate preparation, usually grit blasting, governs it.

---

## Where it wins

| Application | Why |
|---|---|
| **Repair of heat treated parts** | **No HAZ.** The substrate temper is unchanged |
| **Repair of magnesium and aluminium castings** | Which cannot be welded reliably |
| **Corrosion and wear coatings** | Thick, dense, and cold |
| **Dimensional restoration** | Add material and machine back |
| **Field repair** | Portable equipment |
| Oxygen sensitive materials | Titanium sprayed in air, since it does not melt |

**Repairing a heat treated aluminium casting is the flagship case.** Welding it would locally overage the material and risk cracking; cold spray adds material with the substrate never exceeding a few hundred degrees.

**Portable equipment makes field repair possible** in a way no other additive process approaches, and military depot repair is a substantial application.

**It is a repair and coating process rather than a part building one.** Free-standing cold spray structures are made and they are not the mainstream use, because the ductility and the adhesion allowable both argue for using it on a substrate.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Solid state. Nothing melts | The entire point |
| Critical velocity is material specific | 550 to 900 m/s |
| Usable window 1.0 to 1.5x critical | Above it, erosion |
| Particle size 10 to 50 um | Out of spec does not bond |
| **No substrate HAZ** | No equivalent elsewhere |
| Heavily cold worked | Anneal if ductility matters |
| **Adhesion is the design allowable** | Not the deposit strength |
| Grit blast the substrate | It governs adhesion |

---

## Failure modes

**Velocity below critical.** Erosion instead of deposition.

**Velocity too high.** Erosion again.

**Out-of-spec powder size.** No bond.

**Deposit ductility assumed.** It is heavily cold worked.

**Cohesive strength used as the allowable.** Adhesion governs.

**Substrate not prepared.** Poor adhesion.

**Helium cost omitted.** It is a large fraction of the operating cost.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM F3339** | Cold spray deposition of metals |
| **MIL-STD-3021** | Materials deposition, cold spray |
| ASTM C633 | Adhesion or cohesion strength of thermal spray coatings |
| ISO/ASTM 52900 | Additive manufacturing terminology |
| ASTM B962 | Density measurement |
| ASTM E2109 | Determining area percentage porosity in thermal sprayed coatings |

---

## References

1. Champagne, V. K. (ed.), *The Cold Spray Materials Deposition Process*, Woodhead, 2007.
2. Assadi, H. et al., "Cold Spraying: A Materials Perspective", *Acta Materialia*, Vol. 116, 2016.
3. MIL-STD-3021, *Materials Deposition, Cold Spray*.
