[Home](../../README.md) > Water Hammer and Hazards

# Water Hammer and Hazards

## Contents

- [Overview](#overview)
- [Governing physics](#governing-physics)
  - [Joukowsky surge](#joukowsky-surge)
  - [Wave speed](#wave-speed)
  - [Pipe period and slow closure](#pipe-period-and-slow-closure)
  - [Column separation](#column-separation)
- [Propulsion-specific transients](#propulsion-specific-transients)
  - [Priming and dead-head surge](#priming-and-dead-head-surge)
  - [Cryogenic chilldown surge](#cryogenic-chilldown-surge)
  - [Adiabatic compression and oxygen ignition](#adiabatic-compression-and-oxygen-ignition)
- [Mitigation](#mitigation)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Operations](#operations)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Water hammer is the most destructive thing an operator can do to a fluid system by accident, and it is entirely predictable.

When a valve closes, the momentum of the moving liquid column has to go somewhere, and it goes into pressure. The surge is large: water at 3 m/s in a steel line produces about 4 MPa, which is far above most feed system operating pressures and quite capable of bursting a line, destroying a pressure transducer, or unseating a joint.

The three variables are:

1. **How fast the velocity changes.** Faster than the pipe period `2L/a` gives the full surge.
2. **How much velocity there is to lose.** The surge is linear in `dV`, which is the reason line velocity limits exist.
3. **What the line is made of, and what is in it.** Wall compliance and especially entrained gas cut the wave speed and therefore the surge.

This document also covers three transients that are specific to propulsion and are not in the classical water hammer literature: priming surge, cryogenic chilldown surge, and adiabatic compression, which is an ignition hazard rather than a structural one.

---

## Governing physics

### Joukowsky surge

```
dP = rho * a * dV
```

This is the maximum possible surge, produced by any velocity change faster than the pipe period.

**It does not depend on the line length.** A one metre line and a hundred metre line produce the same peak surge from the same velocity change; what length changes is the duration of the pulse and how slowly you have to close to avoid it.

Scale, for `dV = 1 m/s`:

| Fluid | rho [kg/m^3] | a [m/s] (thick steel) | dP per m/s |
|---|---|---|---|
| Water | 998 | 1400 | 1.40 MPa |
| Hydrazine | 1008 | 2050 | 2.07 MPa |
| RP-1 | 810 | 1300 | 1.05 MPa |
| LOX | 1141 | 900 | 1.03 MPa |
| LN2 | 807 | 850 | 0.69 MPa |
| LH2 | 71 | 1100 | 0.078 MPa |

Two things stand out. **Hydrazine is the worst common propellant** for water hammer, because it has both a high density and a very high bulk modulus. And **liquid hydrogen is almost harmless** in this respect, because its density is so low. That is one of the very few things that is easier about hydrogen.

### Wave speed

```
a = sqrt( (K / rho) / ( 1 + (K*D)/(E*t) * c1 ) )
```

The numerator is the acoustic speed in the unconfined fluid. The denominator corrects for pipe wall compliance: a pipe that strains radially stores part of the pressure pulse as wall deflection, which slows the wave.

| Term | Meaning |
|---|---|
| `K` | Fluid isentropic bulk modulus [Pa]. Equal to `rho * c^2` |
| `E` | Pipe elastic modulus [Pa] |
| `D`, `t` | Pipe inner diameter and wall thickness |
| `c1` | Restraint factor: 1.0 anchored upstream only, 0.91 anchored throughout |

**Entrained free gas is the dominant effect when it is present.** The mixture bulk modulus is

```
1/K_mixture = (1 - alpha)/K_liquid + alpha/K_gas
```

and the gas bulk modulus is just its absolute pressure, thousands of times smaller than the liquid's. The result:

| Free gas fraction | Wave speed (water, 50 mm steel line, 1 MPa) | Joukowsky surge at 3 m/s |
|---|---|---|
| 0 | 1360 m/s | 4.08 MPa |
| 0.1 % | 807 m/s | 2.42 MPa |
| 1 % | ~300 m/s | ~0.90 MPa |

**0.1 percent free gas by volume cuts the surge by 40 percent.** That is the mechanism an accumulator uses deliberately. It is also a trap: a line that has not been fully bled behaves nothing like the calculation, the surge is much smaller than predicted, and everyone concludes the analysis was conservative. Then the line is properly bled before flight and the surge appears.

### Pipe period and slow closure

The pressure wave travels from the valve to the nearest large volume (a tank, a manifold, a reservoir) and reflects back. The round trip takes

```
t_pipe = 2 * L / a
```

**If the closure time is shorter than `t_pipe`**, the reflected wave has not returned by the time the valve is shut, no cancellation occurs, and the full Joukowsky surge is produced.

**If the closure time is longer**, the returning wave partially cancels the surge as it builds, and the Michaud (or Allievi) relation applies:

```
dP = rho * L * dV / t_closure
```

Doubling the closure time halves the surge, but **only once you are past the pipe period**. Below it, slowing the valve buys nothing at all. This is the single most useful practical result in the topic, and it is the reason the pipe period is the first number to compute.

**The effective closure time is not the valve stroke time.** A valve with an equal-percentage or quick-opening characteristic does most of its flow reduction in the last part of its travel, so the time over which the velocity actually changes can be a small fraction of the stroke time. A nominally "slow" two-second butterfly valve that goes from 20 percent flow to zero in the last 50 ms produces a full Joukowsky surge. Compute the effective time from the characteristic curve, not from the actuator specification.

### Column separation

The negative half of the surge is the one that causes catastrophic failures.

A valve closing at the downstream end of a line produces a positive surge upstream and a negative surge downstream. A pump trip produces a negative surge first. If the negative excursion takes the local pressure below the fluid vapor pressure, the liquid column separates: a vapor cavity forms and the two columns move apart.

Then the pressure recovers, drives the columns back together, and they collide. **There is no gas cushion between them.** The rejoining impact is a liquid-on-liquid collision at the full separation velocity, and the resulting spike is routinely **two to five times** the original Joukowsky surge.

This is the mechanism behind most catastrophic water hammer failures. The original transient is survivable; the cavity collapse is not.

Column separation is most likely:

- At local high points in a routing, where the static pressure is lowest
- Immediately downstream of a closing valve
- In any system already operating at low static pressure
- On pump trip, where the negative wave arrives first

The design responses are to avoid local high points in liquid lines, to put vent or vacuum-breaker valves at any high point that cannot be avoided, and to keep the static pressure high enough that the negative excursion cannot reach vapor pressure.

---

## Propulsion-specific transients

### Priming and dead-head surge

**Priming surge** happens on valve OPENING, not closing. When a fast valve opens into an empty or gas-filled downstream line, the liquid accelerates into the line, travels down it, and slams into the closed end or into the injector face. The impact velocity can be much higher than the steady-state flow velocity because there was nothing resisting the acceleration.

This is a known failure mode for:

- Upper stage engine start, where the propellant valve opens into a dry line and the surge hits the injector
- Any dead-ended branch that is filled by opening a valve
- Fill and drain operations

The mitigation is a **soft-start valve**: a profiled opening that limits the acceleration, or a small bypass valve opened first to fill the line slowly before the main valve opens.

**Dead-head surge** is the same event at the other end: a pump or a pressurized supply driving into a closed valve. The pressure rises to the supply pressure plus whatever surge the deceleration produced.

### Cryogenic chilldown surge

A cryogenic line being chilled down does not contain liquid. It contains alternating slugs of liquid and vapor, generated by the liquid flashing on the warm wall. Each liquid slug is accelerated by the expanding vapor behind it, and each arrival at a bend or a closed valve is a small water hammer event.

The characteristics that make it dangerous:

- The slug velocities can be **much higher** than the steady-state flow velocity, because the vapor generation accelerates them
- It happens **repeatedly**, thousands of times over a chilldown, so it is a fatigue exposure
- It is **not predicted** by a steady-state model, because there is no steady state during chilldown

The mitigations are to chill down slowly with a restricted flow, to chill from the bottom up so vapor can escape upward, and to size the line velocity limit for chilldown (3 m/s two-phase) rather than for the run condition.

### Adiabatic compression and oxygen ignition

This is not a structural failure mode. It is an **ignition** mechanism, and it is the reason oxygen system valves are opened slowly.

When a valve opens rapidly into a dead-ended downstream volume, the gas already in that volume is compressed by the incoming high-pressure gas far faster than it can lose heat to the walls. The compression is adiabatic:

```
T2 = T1 * (P2/P1)^((gamma-1)/gamma)
```

| Compression | Final temperature from 293 K |
|---|---|
| 1 atm to 3.5 MPa | 800 K |
| 1 atm to 10 MPa | 1090 K |
| 1 atm to 20 MPa | 1330 K |
| 1 MPa to 20 MPa | 690 K |

Autoignition temperatures in oxygen, indicative:

| Material | Ignition temperature in oxygen |
|---|---|
| Hydrocarbon oil or grease | ~500 K |
| Viton (FKM) | ~590 K |
| PCTFE (Kel-F) | ~660 K |
| PTFE | ~780 K |
| Aluminum | ~1000 K |
| Carbon steel | ~1600 K |
| 316 stainless | ~1700 K |
| Monel | ~2200 K |

Opening a valve from atmosphere into a 20 MPa GOX system reaches 1330 K, which is above the ignition temperature of every non-metal in use and above that of aluminum. The classic accident is a fast-acting valve opened into a dead-ended line containing a polymer seat or a trace of hydrocarbon contamination.

**Mitigations:**

- Open oxygen valves slowly, at a defined and verified rate
- Use a small bypass valve to equalize pressure before opening the main valve
- Eliminate dead-ended volumes downstream of fast valves
- Use only oxygen-compatible materials in any volume that can be adiabatically compressed
- Keep the system scrupulously clean; hydrocarbon contamination lowers the threshold dramatically

The same mechanism heats trapped gas in hydrazine and hypergolic systems, where the concern is thermal decomposition of the propellant rather than combustion of a polymer.

---

## Mitigation

| Mitigation | Residual surge fraction | How it works | Cost |
|---|---|---|---|
| Slow closure (5x pipe period) | 0.20 | Reflected wave cancellation | Response time; may conflict with safety shutoff requirements |
| Gas-charged accumulator adjacent to the valve | 0.15 | Provides local compliance so the wave has somewhere to go | Mass, a bladder with a life limit, a precharge to maintain |
| Surge tank / standpipe | 0.10 | Open volume absorbs the wave | Ground systems only |
| Fast-acting surge relief valve | 0.40 | Vents the peak | Limited by its own response time, which is often slower than the wave |
| Soft-start / profiled valve | 0.25 | Limits the acceleration on opening | Addresses priming surge specifically |
| Restricting orifice in the line | 0.60 | Damps the wave through dissipation | Costs steady-state pressure permanently |
| **Reduce the line velocity** | Linear in `dV` | Attacks the root cause | Larger line, more mass, more residual |
| Accept it and thicken the wall | 1.00 | Survives rather than avoids | Mass; and it does not address column separation |

**The accumulator is usually the right answer** when a fast closure is genuinely required. It must be adjacent to the valve, on the upstream side, because the wave has to reach it before it reaches anything fragile. An accumulator ten metres upstream protects the ten metres beyond it and nothing between it and the valve.

**Reducing velocity is the most robust mitigation** because it is linear and it has no failure modes. It is also the most expensive in mass. This is the trade behind the line velocity limits in [PipeRoutingAndSizing.md](PipeRoutingAndSizing.md).

---

## Design rules of thumb

| Rule | Value | Why |
|---|---|---|
| Joukowsky surge scale | ~1.4 MPa per m/s in water, ~2.1 in hydrazine | Memorize one number and scale |
| Surge is independent of line length | Always | Length sets the duration and the closure time you need |
| Slow closure threshold | `t_close > 2L/a` | Below the pipe period, slowing the valve does nothing |
| Effective closure time | From the characteristic, not the stroke time | Quick-opening trim closes the flow in the last few percent |
| Entrained gas at 0.1 % | Cuts the surge by ~40 % | And makes any measurement unrepresentative |
| Column separation multiplier | 2 to 5x the original surge | The failure mode that actually breaks things |
| Design the negative excursion above vapor pressure | Always | Prevents separation entirely |
| Accumulator placement | Adjacent to the valve, upstream | It only protects what is beyond it |
| Fill line velocity | <= 5 m/s | Limits the stored kinetic energy |
| Cryogenic chilldown velocity | <= 3 m/s two-phase | Slug velocities exceed the mean |
| Oxygen valve opening | Slow, defined rate, no dead legs | Adiabatic compression ignition |
| Surge is a fatigue exposure | Every cycle counts | Not a one-off static check |

---

## Failure modes

**Line burst.** The obvious one, and the least common in practice because most lines have large wall margins from handling requirements.

**Instrumentation destruction.** A pressure transducer with a 10 MPa range sees a 15 MPa spike and is scrapped. Very common, and often the first indication that surge is occurring.

**Joint unseating.** A flare or a compression joint that survives the static pressure loosens under the repeated impulsive load. Shows up as a slow leak that appears after a series of tests.

**Support and bracket failure.** The unbalanced pressure force during the transient acts on every bend and every closed end. A line with adequate supports for steady flow can tear its brackets off during a surge, because the transient force is much larger.

**Column separation cavity collapse.** The catastrophic case. Usually destroys the line at the rejoining location, which is often not where the valve is.

**Bellows and flex hose failure.** A bellows sees the surge as an axial pressure thrust and it is the most compliant thing in the line, so the transient displacement concentrates there.

**Valve internal damage.** The valve that caused the surge sees it too, on its seat and its stem.

**Fatigue.** Surge is repeated on every cycle of the system. A line that survives one surge with a factor of 1.2 on stress will not survive ten thousand of them.

**Oxygen ignition from adiabatic compression.** The non-structural failure mode, and by far the most dangerous.

---

## Operations

**Instrument for it.** A high-frequency pressure transducer (at least 10 kHz sampling) at the valve and at the far end of the line. Surge is a millisecond event and a 10 Hz data system will not see it at all; it will show a slightly elevated steady pressure and nothing else.

**Verify the effective closure time by test**, not by specification. Command the valve closed and record the flow and pressure traces.

**Bleed the line completely before any surge-relevant test**, and record that it was bled. A partially bled line gives an optimistic result.

**Sequence valve operations deliberately.** Closing two valves simultaneously in series can trap a column between them with no relief path.

**Open slowly, close according to the analysis.** Opening is a priming surge risk and closing is a Joukowsky risk, and they have different mitigations.

**On any oxygen system, open valves slowly and verify no dead legs.** This is a procedural control that substitutes for a design feature, and procedural controls fail. Design the dead legs out.

---

## Worked example

Water at 3 m/s in a 50 mm ID, 3 mm wall 316L line, 20 m from the valve back to the tank, line pressure 1.0 MPa, valve closure time 500 ms.

**Wave speed and pipe period:**

| Quantity | Value |
|---|---|
| Density | 998.6 kg/m^3 |
| Bulk modulus | 2.199 GPa |
| **Wave speed** | **1360.3 m/s** |
| **Pipe period 2L/a** | **29.4 ms** |

**Surge:**

| Quantity | Value |
|---|---|
| Joukowsky surge (instantaneous) | 4.075 MPa (591 psi) |
| Closure time | 500 ms |
| Rapid closure? | No, 500 ms >> 29.4 ms |
| **Actual surge (Michaud)** | **0.120 MPa (17.4 psi)** |
| Peak pressure | 1.120 MPa |
| Minimum pressure | 0.880 MPa |
| Vapor pressure | 2.34 kPa |
| Column separation | No |
| Hoop stress at peak | 9.33 MPa |
| Stress margin | 12.1 |

The 500 ms closure is 17 times the pipe period, so the surge is reduced by a factor of 34 from the Joukowsky value. That is the whole benefit of slow closure and it is why the closure time is a design requirement rather than a free parameter.

**Required closure time for a 2.0 MPa peak limit:** 59.9 ms. Note that this is still twice the pipe period, so slow-closure reduction is available. If the requirement had been 4.0 MPa peak the answer would have been below the pipe period, and the class would warn that slow closure cannot help.

**With 0.1 percent entrained gas:** wave speed falls to 807 m/s and the Joukowsky surge falls to 2.42 MPa. The line looks much safer than it is, until it is properly bled.

Reproduce with:

```python
from WaterHammer import WaterHammer

surge = WaterHammer()
surge.setInputs({'fluid': 'Water', 'pressure': 1.0e6, 'temperature': 293.15,
                 'velocity': 3.0, 'innerDiameter': 0.05, 'wallThickness': 0.003,
                 'length': 20.0, 'material': '316L', 'closureTime': 0.5})

surge.calculateSurge()
print(surge.generateReport())
print(surge.requiredClosureTime(2.0e6))
print(surge.calculateAdiabaticCompression(101325.0, 20e6, gamma = 1.4))
```

---

## Standards

| Standard | Scope |
|---|---|
| ASME B31.3 para 301.5 | Dynamic effects, including impact and surge |
| AWWA M11 | Steel pipe design, includes surge analysis practice |
| NASA SP-8080 | Liquid rocket pressure regulators, relief valves, check valves, burst disks and explosive valves |
| NASA-STD-8719.17 | Ground-based pressure vessels and pressurized systems |
| ASTM G88 | Designing systems for oxygen service (adiabatic compression guidance) |
| ASTM G72 | Autogenous ignition temperature of materials in oxygen |
| ASTM G74 | Ignition sensitivity of materials to gaseous fluid impact |
| CGA G-4.4 | Oxygen pipeline and piping systems |
| ISO 21010 | Cryogenic vessels, gas/materials compatibility |

---

## Tool interface

The [`WaterHammer`](../WaterHammer.py) class covers wave speed, surge, column separation, required closure time and adiabatic compression.

```python
from WaterHammer import WaterHammer

surge = WaterHammer()
surge.setInputs({'fluid': 'N2H4', 'pressure': 2.3e6, 'temperature': 293.15,
                 'velocity': 2.34, 'innerDiameter': 0.004928, 'wallThickness': 0.000711,
                 'length': 2.5, 'material': '316L', 'closureTime': 0.020,
                 'entrainedGasFraction': 0.0})

surge.calculateWaveSpeed()
surge.calculateSurge()
surge.checkColumnSeparation()
surge.requiredClosureTime(targetPeakPressure = 3.5e6)
surge.calculateAdiabaticCompression(101325.0, 20e6)
print(surge.generateReport())
```

Lookup tables: `WaterHammer.RESTRAINT_FACTORS`, `WaterHammer.MITIGATION_EFFECTIVENESS`.

---

## References

1. Wylie, E. B. and Streeter, V. L., *Fluid Transients in Systems*, Prentice Hall, 1993.
2. Chaudhry, M. H., *Applied Hydraulic Transients*, 3rd ed., Springer, 2014.
3. Thorley, A. R. D., *Fluid Transients in Pipeline Systems*, 2nd ed., Professional Engineering Publishing, 2004.
4. Joukowsky, N., "Uber den hydraulischen Stoss in Wasserleitungsrohren", 1900.
5. Bergant, A., Simpson, A. R. and Tijsseling, A. S., "Water Hammer with Column Separation: A Historical Review", *Journal of Fluids and Structures*, Vol. 22, 2006.
6. ASTM G88-13, *Standard Guide for Designing Systems for Oxygen Service*.
7. NASA SP-8080, *Liquid Rocket Pressure Regulators, Relief Valves, Check Valves, Burst Disks, and Explosive Valves*, 1973.
8. Barron, R. F., *Cryogenic Systems*, 2nd ed., Oxford University Press, 1985 (chilldown transients).
