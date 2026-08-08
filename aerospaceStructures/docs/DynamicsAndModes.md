[Home](../README.md) > Dynamics and Modes

# Dynamics and Modes

## Contents

- [Overview](#overview)
- [The stiffness requirement](#the-stiffness-requirement)
- [Why frequency sizes structure differently](#why-frequency-sizes-structure-differently)
- [Shell modes are the trap](#shell-modes-are-the-trap)
- [Coupled loads analysis](#coupled-loads-analysis)
- [POGO](#pogo)
- [Slosh](#slosh)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A launch vehicle has a minimum frequency requirement before it has a strength requirement, and meeting it is a stiffness problem rather than a strength one. The two size structure in different directions.

---

## The stiffness requirement

**The launch provider states it**, and it is a hard interface requirement.

| Class | Lateral | Axial |
|---|---|---|
| Small launcher | 8 Hz | 20 Hz |
| **Medium launcher** | **10 Hz** | **25 Hz** |
| Large launcher | 15 Hz | 35 Hz |
| Rideshare | 25 Hz | 45 Hz |

**The purpose is separation of modes.** The payload's modes have to stay clear of the vehicle's control bandwidth and of the dominant structural modes, so the coupled loads analysis does not find a resonance that drives the loads up.

**Rideshare requirements are the highest** because the accommodation has less mass and the dispenser is stiffer, so the payload must be stiffer to stay above it.

**It is a requirement on the first mode**, not on a mode of a particular type, which is the source of the trap below.

---

## Why frequency sizes structure differently

```
f = (betaL)^2 / (2 pi L^2) sqrt(E I / m')
```

**Frequency goes as the square root of stiffness over mass**, so doubling it needs four times the stiffness at the same mass. Strength goes linearly with section modulus.

**A structure sized by strength and then found too soft usually has to grow substantially**, which is why the frequency check belongs early. Adding a millimetre of wall for strength is cheap; quadrupling the second moment is not.

**Length dominates.** Frequency goes as `1/L^2`, so halving a cantilever's length quadruples its frequency. Moving a hard point is almost always cheaper than stiffening a member.

**For a thin shell, thickness barely enters at all.** Both `I` and mass per unit length scale linearly with wall thickness, so they cancel: a 2 mm and an 8 mm cylinder of the same radius have nearly the same beam bending frequency. Adding wall to fix a frequency problem on a thin shell does very little.

**Tip mass dominates a cantilever.** For the worked example the tip mass drops the bending frequency by 55 percent, so the structure is mass dominated at the free end and stiffening the root buys less than it appears to.

---

## Shell modes are the trap

**A thin cylinder's lowest mode is usually not the beam bending mode.** It is a shell mode with circumferential waves, and it can sit far below.

| Mode | Frequency |
|---|---|
| **Shell, n = 2 (ovalling)** | **4.62 Hz** |
| Shell, n = 3 | ~12 Hz |
| Shell, n = 4 | ~23 Hz |
| **Beam bending** | **45.00 Hz** |
| Axial | 110 Hz |

**A beam idealisation reports this structure as 9.7x stiffer than it is.** Against a 10 Hz requirement the beam mode gives a margin of **+3.500** and the true first mode gives **-0.538**. That is the difference between passing and failing, and a beam model passes it.

**The n = 2 ovalling mode is the lowest** because the ring bending stiffness that resists it is the smallest for the fewest waves that are not a rigid body motion.

**Ring frames raise shell modes and do nothing for the beam mode.** That is the correct fix and it is not what a beam model would suggest.

---

## Coupled loads analysis

**The vehicle and payload finite element models are combined and run against the forcing functions**, producing the loads the payload actually sees.

| Stage | Detail |
|---|---|
| **Preliminary CLA** | Early, coarse models, sizing loads |
| **Verification CLA** | Final models, test correlated, the loads of record |
| Forcing functions | Liftoff transient, engine ignition, gust, staging, shutdown |

**The frequency requirement exists to make the CLA well behaved.** A payload mode near a vehicle mode produces a large dynamic amplification and loads that may exceed what any reasonable structure carries.

**Model correlation is a requirement, not a courtesy.** A modal survey test correlates the finite element model to measured modes, typically requiring frequency agreement within 3 to 5 percent and cross-orthogonality above 0.9, before the model is accepted for the verification CLA.

---

## POGO

**A closed-loop instability between the structure and the propulsion system.**

The loop: a longitudinal structural oscillation modulates the propellant feed pressure, which modulates the thrust, which drives the structural oscillation. If the phase is unfavourable and the gain exceeds unity, it diverges.

| Element | Role |
|---|---|
| **Structural axial mode** | The oscillation |
| **Feed line dynamics** | Converts motion into pressure |
| **Engine transfer function** | Converts pressure into thrust |
| **Accumulator** | The fix: a gas volume that detunes the feed line |

**The fix is a POGO accumulator**, a deliberately compliant gas volume in the feed line that shifts the feed system resonance away from the structural mode. Adding it is a fluid system change to solve a structural dynamics problem, and it is the clearest coupling between this domain and [fluidSystems](../../fluidSystems/).

**It is not hypothetical.** Gemini-Titan and Apollo both had POGO events, and Apollo 13's second stage centre engine shut down early because of one.

---

## Slosh

**Propellant moving in a partly full tank is a large mass with its own modes.**

| Consequence | Detail |
|---|---|
| **Lateral force and moment** | Fed back into the control system |
| **Frequency near control bandwidth** | Where it interacts badly |
| **Damping is very low** | 0.1 to 0.5 percent without baffles |

**The first slosh mode frequency** for a cylindrical tank scales roughly as `sqrt(g_effective / R)`, so it moves with acceleration through the flight and passes through the control bandwidth rather than sitting outside it.

**Baffles are the fix**, and they are a structural item sized by a dynamics requirement. Ring baffles at the fill line raise the damping by an order of magnitude.

**Slosh mass can be a substantial fraction of the vehicle mass**, so it is modelled as an equivalent pendulum or spring-mass in the control analysis rather than as a rigid mass.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Frequency requirement before strength | It is expensive to fix late |
| `f` goes as `sqrt(EI/m)` | Doubling needs 4x the stiffness |
| `f` goes as `1/L^2` | Shortening beats stiffening |
| Wall thickness barely moves a thin shell's beam mode | `I` and mass both scale with `t` |
| **Check shell modes, not just beam modes** | The n=2 mode is usually lowest |
| Ring frames fix shell modes | And do nothing for the beam mode |
| Model correlation within 3 to 5 percent | Before the verification CLA |
| POGO is fixed in the feed system | An accumulator |

---

## Failure modes

**Beam idealisation used on a thin shell.** 9.7x optimistic for the reference case.

**Frequency checked after sizing.** Expensive late growth.

**Wall added to fix a thin shell frequency.** It barely moves.

**Closed-form estimate trusted to better than 20 percent.** It is not that good.

**Tip mass omitted.** 55 percent error for the reference cantilever.

**Slosh treated as a rigid mass.** It has its own modes near the control bandwidth.

**Uncorrelated model used for the verification CLA.** Not acceptable.

---

## Worked numbers

From [`ModalEstimate`](../aerospaceStructuresLibrary/ModalEstimate.py) on the stage tank, 1.8 m radius, 22.59 mm wall, 6 m cantilever with 4200 kg tip mass:

| Mode | Frequency | Margin against 10 Hz |
|---|---|---|
| **Shell n = 2** | **4.62 Hz** | **-0.538, FAIL** |
| Beam bending | 45.00 Hz | +3.500, PASS |
| Axial | 109.85 Hz | +3.394 against 25 Hz |

**A beam-only check passes this structure at +3.500 when its true first mode fails at -0.538.**

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-5002** | Load analyses of spacecraft and payloads |
| NASA-HDBK-7005 | Dynamic environmental criteria |
| **NASA-STD-7001** | Payload vibroacoustic test criteria |
| SMC-S-016 | Test requirements for launch and space vehicles |
| ECSS-E-ST-32-11 | Modal survey assessment |
| NASA SP-8055 | Prevention of coupled structure-propulsion instability (POGO) |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'aerospaceStructuresLibrary')

from ModalEstimate import ModalEstimate

modes = ModalEstimate()
modes.setInputs({'material': '2219-T87', 'condition': 't87', 'radius': 1.8,
                 'thickness': 0.02259, 'length': 6.0,
                 'boundaryCondition': 'cantilever', 'tipMass': 4200.0,
                 'requiredLateral': 10.0, 'requiredAxial': 25.0})

result = modes.screenAgainstRequirement()
for name, frequency in sorted(result['modes'].items(), key = lambda item: item[1]):
    print(f'{name:20s} {frequency:8.2f} Hz')
for finding in result['findings']:
    print(finding)
```

---

## References

1. Blevins, R. D., *Formulas for Natural Frequency and Mode Shape*, Krieger, 1979.
2. NASA SP-8055, *Prevention of Coupled Structure-Propulsion Instability (POGO)*, 1970.
3. Abramson, H. N., *The Dynamic Behavior of Liquids in Moving Containers*, NASA SP-106, 1966.
