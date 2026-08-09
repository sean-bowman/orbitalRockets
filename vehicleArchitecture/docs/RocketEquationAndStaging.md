[Home](../README.md) > Rocket Equation and Staging

# Rocket Equation and Staging

## Contents

- [Overview](#overview)
- [The equation, and the bookkeeping that goes wrong](#the-equation-and-the-bookkeeping-that-goes-wrong)
- [The structural coefficient, and its denominator](#the-structural-coefficient-and-its-denominator)
- [The delta-V ceiling nobody mentions](#the-delta-v-ceiling-nobody-mentions)
- [Optimal staging](#optimal-staging)
- [The optimum is flat](#the-optimum-is-flat)
- [The real vehicle is not at it](#the-real-vehicle-is-not-at-it)
- [Serial, parallel and drop tanks](#serial-parallel-and-drop-tanks)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Tsiolkovsky is the easy part of vehicle design and it gets most of the attention.

```
dV = c ln(m0 / mf)
```

What is hard is everything that decides `mf`, and what is subtle is that the equation applied across stages has bookkeeping in it that produces plausible wrong answers.

---

## The equation, and the bookkeeping that goes wrong

**Each stage lifts everything above it.** The initial mass of stage one is its own gross mass plus every stage above it plus the payload; its burnout mass is that less its own propellant, and it still includes its own dry mass because the stage has not separated yet.

Getting that wrong does not produce an error. It produces a number that is a few per cent off, which is inside the range a reasonable person would accept.

The check that catches it is external: put real published stage masses through the implementation and see whether the answer lands near a real mission requirement. See [ValidationReferences](ValidationReferences.md).

---

## The structural coefficient, and its denominator

```
eps = dry stage mass / gross stage mass
```

**Note the denominator.** Some sources define it against propellant mass instead, and the two differ by enough to change a design: at a coefficient of 0.05 against gross mass, the same stage is 0.053 against propellant. Small, and it compounds through a sizing loop.

This repository uses gross mass throughout, and a test asserts the published reference cases are read the same way.

Real values, carried in the library as bands:

| Architecture | Coefficient |
|---|---|
| Kerolox booster | 0.045 to 0.070 |
| Kerolox upper stage | 0.030 to 0.055 |
| Hydrolox upper stage | 0.080 to 0.120 |
| Pressure fed | 0.080 to 0.150 |

Hydrogen is bulky and the tank pays for it, which is why a hydrolox upper stage carries twice the structural coefficient of a kerolox one and still wins on specific impulse.

---

## The delta-V ceiling nobody mentions

A stage cannot exceed a mass ratio of `1/eps` however much propellant it carries, because at that ratio the stage is all structure and no propellant.

So there is a hard delta-V ceiling per stage:

```
dV_max = c ln(1 / eps)
```

At a coefficient of 0.05 and an exhaust velocity of 3000 m/s, that is 8987 m/s. **A single stage at those numbers cannot reach orbit no matter what**, and that is the real argument for staging: not efficiency, but reachability.

[StagedVehicle](RocketEquationAndStaging.md) reports that ceiling in its error message when a target is unreachable, because knowing the target is impossible is more useful than knowing the solve failed.

---

## Optimal staging

Maximising payload for a fixed total delta-V gives, by Lagrange multipliers, a condition on each stage's mass ratio:

```
n_i = (c_i L - 1) / (c_i L eps_i)
```

with one multiplier `L` shared across the stages, chosen so the delta-V sums to the target. That is one scalar equation in one unknown.

**Two implementation traps, both of which shipped here and were caught by tests.**

The total delta-V rises monotonically with `L`, so a bisection has to move the upper bracket down when the total is too high. Running it the other way converges to the wrong end and returns a split that does not sum to the target.

The admissible range of `L` starts where every stage's mass ratio exceeds one, at `L > max 1/(c_i (1 - eps_i))`. Searching for that boundary by stepping upward overshoots it, skipping the region containing the answer and pinning the optimiser at a corner. **Compute the boundary rather than searching for it.**

---

## The optimum is flat

This is the result worth having.

On the reference vehicle, shifting ten per cent of the first stage delta-V either way from the optimum costs at most **0.20 per cent of liftoff mass**.

**The optimisation is worth doing once and it is not worth defending.** An argument about the staging split is almost always an argument about the wrong thing, and the same hour spent on the tank would be worth an order of magnitude more. See [MassChain](MassChain.md).

---

## The real vehicle is not at it

Falcon 9 puts about 40 per cent of its delta-V on the first stage. The payload optimum for its published coefficients and engine performance wants about 28 per cent.

Sizing it optimally would save under four per cent of liftoff mass.

**That four per cent buys things the optimisation cannot see**: engine commonality between the stages, a first stage that comes back, and a staging altitude and velocity the recovery needs. A vehicle at its theoretical staging optimum would be a worse vehicle.

That is worth stating plainly because it is the general case rather than an exception. **The staging optimum is a starting point, and every real constraint moves it.**

---

## Serial, parallel and drop tanks

The library covers serial staging. The others are named here rather than modelled, with what each buys.

**Parallel staging** fires boosters and core together and drops the boosters early. It buys liftoff thrust without a large first stage, and it costs a core stage that burns at a poor mixture of altitudes. The rocket equation applies per burn phase rather than per stage, which is why a parallel vehicle is not modelled by the class here.

**Crossfeed** feeds the core from the boosters so the core is full at booster separation, which makes the core effectively an upper stage. It is a large performance gain and it has never flown, because the plumbing crosses a separation plane at full flow.

**Drop tanks** are the limiting case of staging: jettison structure without jettisoning an engine. They buy most of the staging benefit for none of the engine cost and they cost a structural joint that has to hold and then let go.

All three are the same idea, which is that carrying empty structure is what staging exists to stop.

---

## Worked numbers

Falcon 9 Block 5 from published masses.

| Quantity | Stage 1 | Stage 2 |
|---|---|---|
| Dry mass | 22,200 kg | 4,000 kg |
| Gross mass | 433,100 kg | 111,500 kg |
| Structural coefficient | 0.0513 | 0.0359 |
| Mass ratio at 22.8 t payload | 3.626 | 5.011 |
| Delta-V | 3751 m/s | 5500 m/s |

Total 9252 m/s at a liftoff mass of 567 t, against a low Earth orbit requirement of about 9300.

---

## Design rules of thumb

- **Check the bookkeeping against a real vehicle.** Stage-lifts-everything-above is easy to get wrong and it fails quietly.
- **State the denominator** when quoting a structural coefficient.
- **Check the ceiling before optimising.** `c ln(1/eps)` per stage, and no propellant load beats it.
- **Optimise the split once and then stop.** It is flat and every real constraint moves it anyway.
- **Spend the effort on the coefficient**, which is where the payload actually is.

---

## Failure modes

**Stage mass bookkeeping.** Produces a plausible number rather than an error.

**A structural coefficient against the wrong denominator.** Small, and it compounds through a sizing loop.

**A bisection run the wrong way.** Shipped here. It returned a split that did not sum to the target, and only an assertion on the sum caught it.

**A bracket search that overshoots an admissible boundary.** Also shipped here, from the same method, and it pinned the optimiser at a corner.

**Defending the staging optimum.** It is flat, and the vehicle you are arguing with is probably right for reasons outside the model.

---

## Tool interface

```python
from StagedVehicle import StagedVehicle

vehicle = StagedVehicle()
vehicle.setInputs({'stages': [{'specificImpulse': 297.0, 'structuralCoefficient': 0.0513},
                              {'specificImpulse': 348.0, 'structuralCoefficient': 0.0359}],
                   'payloadMass':  22800.0,
                   'targetDeltaV': 9252.0})

optimal  = vehicle.optimiseStaging()
sized    = vehicle.sizeToDeltaV()
flatness = vehicle.checkStagingFlatness()

print(vehicle.generateReport())
```

Supply `propellantMass` per stage instead of `targetDeltaV` to analyse a defined vehicle with `calculatePerformance()`.

---

## References

- Tsiolkovsky, and every text since
- Curtis, *Orbital Mechanics for Engineering Students*, for the Lagrange staging condition
- Humble, Henry and Larson, *Space Propulsion Analysis and Design*
- [ValidationReferences](ValidationReferences.md), for the Falcon 9 masses used above
