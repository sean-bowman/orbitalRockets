[Home](../README.md) > Thermal Modelling

# Thermal Modelling

## Contents

- [Overview](#overview)
- [The nodal formulation](#the-nodal-formulation)
- [Implicit or explicit](#implicit-or-explicit)
- [Radiation makes the network nonlinear](#radiation-makes-the-network-nonlinear)
- [How many nodes](#how-many-nodes)
- [Run length, and the peak that is not a peak](#run-length-and-the-peak-that-is-not-a-peak)
- [Soakback](#soakback)
- [Where the uncertainty lives](#where-the-uncertainty-lives)
- [Model correlation](#model-correlation)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A thermal model is a set of lumps connected by resistances, marched through time. The formulation is old, simple and adequate for nearly everything a launch vehicle needs. Almost every wrong answer it produces comes from a modelling decision rather than from the physics: how many nodes, how long to run, what to do about radiation, and what to lump with what.

This document is about those decisions.

---

## The nodal formulation

Each node has a capacitance and an energy balance:

```
C_i dT_i/dt = Q_i + sum over j of (T_j - T_i) / R_ij
```

Assembled over all free nodes this is `C dT/dt = Q - K T`, with `K` the conductance matrix. Boundary nodes have a fixed temperature and move to the right hand side.

**A node with no capacitance is an arithmetic node.** It has no thermal mass and simply balances the heat arriving at it. That is a useful idealisation for a thin surface or an interface, and it cannot be marched in time, because a zero capacitance makes `C/dt` singular. The [ThermalNetwork](#tool-interface) class refuses it explicitly rather than producing a matrix that fails obscurely.

**A node connected to nothing is an undetermined temperature.** The conductance matrix is singular, and the error message that matters is the one that says which node is disconnected rather than the one that says the matrix is singular.

---

## Implicit or explicit

The march can be forward Euler, which is explicit and cheap per step, or backward Euler, which is implicit and requires a solve.

```
explicit:  T_new = T_old + dt/C (Q - K T_old)
implicit:  (C/dt + K) T_new = C/dt T_old + Q
```

**Explicit is stable only below a time step set by the smallest node's time constant**, `dt < 0.5 C_min / K_min`. That limit is the reason implicit wins on a real vehicle model.

Consider a network containing a 2 mm skin and a 22 kg bulkhead. The skin's time constant is seconds; the bulkhead's is tens of minutes. **An explicit march has to take the skin's time step for the entire run**, which for a soakback case running to 6000 seconds means hundreds of thousands of steps to resolve a bulkhead that changes over hours.

Backward Euler is unconditionally stable, so the time step is chosen by accuracy rather than by stability. It costs one matrix solve per step, and on a network of tens of nodes that is nothing.

The stability limit is still worth reporting even when it is not being used, because it is the physical timescale of the fastest node and a step much larger than it is resolving that node badly even though it is not diverging.

---

## Radiation makes the network nonlinear

A radiative link is not a resistance. It is `eps sigma A (T_h^4 - T_c^4)`, and to appear in a linear system it has to be written as a conductance:

```
h_r = eps sigma (T_h + T_c)(T_h^2 + T_c^2)
```

That expression is exact at the temperatures used to form it. **It is the temperatures that are the problem, because they are what the solve is trying to find.**

Two consequences, and both were bugs in this library before they were features.

**A steady state solve has to iterate.** Linearise about the current temperatures, solve, re-linearise about the answer, solve again, until the temperatures stop moving. Without the iteration the answer depends on whatever the nodes were initialised to, which is not a property a steady state solution is allowed to have.

The size of that error is not small. A single node with a 20 W load radiating to a 250 K boundary has a closed form answer of 278.10 K. Frozen at the initial guess, the solver returned:

| Initial guess [K] | Frozen answer [K] | Error |
|---|---|---|
| 255 | 282.22 | +4.1 |
| 293 | 275.73 | -2.4 |
| 400 | 264.35 | -13.7 |
| 1000 | diverged further | |

**Iterating lands on 278.0954 K from every one of those starts**, within 1e-05 K, in eight to ten passes.

**A transient has to re-form the link at every step.** A soakback case moves hundreds of kelvin, and a conductance formed at the initial temperature understates the rejection as the node heats. In the worked example that error was 5.2 K on the avionics peak and 134 seconds on when it occurred, both in the unconservative direction for the timing and the conservative direction for the temperature.

The transient uses a lagged linearisation: the conductance for step `n` is formed from the temperatures at the end of step `n-1`. That is the standard compromise, it costs one assembly per step, and it is far better than freezing.

---

## How many nodes

The Biot number answers this, and the answer is usually fewer than expected.

```
Bi = h L / k
```

Below 0.1 the body is nearly isothermal and one node is honest. Above it, the number of nodes needed goes roughly as the Biot number, because that is what it takes to resolve the internal gradient.

**The check has to be recorded rather than assumed.** `checkLumpedCapacitance` returns the Biot number, whether the lump is valid, and a suggested node count, so that a single node model carries the evidence that a single node was defensible.

The trap is that the same part can be a lump in one case and not in another. Aluminium at `h` = 500 W/m^2 K on a 5 mm length gives `Bi` = 0.015. Stainless in identical geometry gives 0.154. **Same drawing, same environment, different answer**, because the conductivity differs by a factor of ten.

---

## Run length, and the peak that is not a peak

**If a node's maximum falls at the last time step, it is not a maximum. It is where the run stopped.**

This is the single most consequential detail in the whole domain, and it is invisible unless the solver looks for it. A run that stops while a node is still rising reports a number that is lower than the truth, in a direction that looks like margin.

The detection is trivial and it has to be there. From `_analyseTransient`:

```
stillRising = [name for name, entry in peaks.items()
               if np.isclose(entry['peakTime'], times[-1]) and entry['rise'] > 0.0]
```

The [worked example](../codeInterface.py) is built around it. Stopping at 150 seconds, when the heating stops, reports the avionics at 307.4 K against a 323.15 K limit and passes. Running to 6000 seconds reports 374.8 K and fails. **The short run flags itself as truncated, and that flag is the only thing standing between the analysis and a wrong answer.**

---

## Soakback

Soakback is the case where a node reaches its maximum after the heating event has ended. It is not an edge case. On any vehicle with protection between a heat source and something temperature sensitive, it is the normal behaviour.

The mechanism is straightforward. During the event, the protection absorbs heat and the interior is shielded from it. After the event, the protection is the hottest thing in the assembly and the only path for its stored energy is inward, because the external environment has gone.

`findSoakback(eventEndTime)` splits each node's history at the event boundary and reports the peak on each side.

| Node | Peak during [K] | Peak after [K] | Peak at [s] | Soaks back |
|---|---|---|---|---|
| TPS backface | 661.9 | 661.9 | 140 | No |
| Bulkhead | 315.7 | 374.6 | 890 | Yes |
| Avionics | 305.3 | 374.8 | 950 | Yes |

**The TPS backface peaks when the heating stops. Everything behind it peaks between six and seven times later.** The deeper the node, the later the peak, which is fixed by the topology rather than by the numbers.

---

## Where the uncertainty lives

A model has many inputs and a few of them decide the answer. `resistanceSensitivity()` reports the fraction of the total series resistance each element carries.

| Element | Share |
|---|---|
| Bulkhead to sink, radiation | 80.4 % |
| Bulkhead to TPS backface, bolted bare vacuum | 16.2 % |
| Avionics to bulkhead, bolted with grease | 3.4 % |

**Anything below about 5 per cent cannot move the answer**, no matter how carefully it is characterised. That threshold is reported rather than left implicit, because effort spent on a 3 per cent resistance is effort not spent on the 80 per cent one.

The counterpoint is that the contact interfaces here carry 20 per cent between them and contact conductance spans a factor of forty across joint types. **The small share is also the least certain share**, so the sensitivity report is a starting point rather than a verdict.

---

## Model correlation

A model that has not been correlated against test data is a prediction, not an analysis. The correlation process is:

1. Run the thermal balance test and record steady temperatures at every sensor.
2. Run the model at the same boundary conditions.
3. Adjust the uncertain parameters, which are the contact conductances and the effective insulation conductivity, until predicted and measured agree.
4. Re-run the transient cases with the correlated parameters.

**The parameters adjusted have to be the uncertain ones.** Adjusting a conductivity that is known to 2 per cent in order to match a temperature that is off by 10 K is fitting, not correlating, and it produces a model that matches one test and predicts nothing.

The usual acceptance is agreement within 3 to 5 K at every sensor in steady state, and the usual reason a model fails it is a contact interface that is not what the drawing said.

---

## Design rules of thumb

- **Use an implicit march.** The explicit stability limit is set by the fastest node and it is punitive on a mixed network.
- **Run until every node turns over**, and check the truncation flag rather than trusting the maximum.
- **Iterate the steady state when radiation is present.** A single pass depends on the initial guess.
- **Re-form radiative links during a transient.** A frozen linearisation is wrong by degrees over a large swing.
- **Check Biot before lumping**, and keep the check.
- **Look at the resistance shares before refining anything.**
- **Correlate against thermal balance data**, adjusting the parameters that are actually uncertain.

---

## Failure modes

**Truncated run reported as a peak.** The defining failure of the domain.

**Frozen radiation linearisation.** Answer depends on the initial guess in steady state; wrong by degrees in a transient.

**Explicit march at too large a step.** Diverges, usually visibly, which is at least honest.

**Explicit march at a step small enough to be stable and too large to resolve.** Does not diverge, and is quietly inaccurate.

**Lumping a high Biot body.** Reports an average, hides the surface.

**A node connected to nothing.** Singular matrix, and the useful error names the node.

**A zero capacitance node in a transient.** Cannot be marched, and should be rejected rather than regularised silently.

**Correlating by adjusting well known parameters.** Produces a model that matches the test and predicts nothing.

---

## Worked numbers

Single node, 20 W load, emissivity 0.85 over 0.2 m^2, radiating to a 250 K boundary. Closed form 278.0954 K.

| Initial guess [K] | Frozen linearisation [K] | Iterated [K] |
|---|---|---|
| 255 | 282.22 | 278.0954 |
| 293.15 | 275.73 | 278.0954 |
| 400 | 264.35 | 278.0954 |
| 1000 | worse still | 278.0954 |

Convergence takes 8 to 10 iterations to within 1e-05 K.

Worked example transient, 140 s heat pulse:

| Quantity | Value |
|---|---|
| Avionics peak, run stopped at 150 s | 307.4 K, flagged truncated |
| Avionics peak, run to 6000 s | 374.8 K |
| Avionics limit | 323.15 K |
| Avionics peak time | 950 s, 6.8 times the event duration |
| Bulkhead peak time | 890 s |
| TPS backface peak time | 140 s, at the end of the pulse |

---

## Standards

| Standard | What it gives you |
|---|---|
| ECSS-E-ST-31C | Thermal control general requirements, including model fidelity |
| ECSS-E-ST-31-04C | Thermal analysis, and the reduced model exchange format |
| NASA-STD-7009 | Standard for models and simulations, the credibility assessment |
| ECSS-E-ST-10-03C | Testing, which is where correlation data comes from |

---

## Tool interface

```python
from ThermalNetwork import ThermalNetwork

network = ThermalNetwork()
network.setInputs({'timeStep': 2.0, 'endTime': 6000.0})

network.addNodeFromMass('skin',     mass = 4.0,  specificHeat = 1900.0, temperature = 293.15)
network.addNodeFromMass('bulkhead', mass = 22.0, specificHeat = 900.0,  temperature = 293.15)
network.addNode('sink', temperature = 250.0, boundary = True)

network.addContact('skin', 'bulkhead', area = 0.040, jointType = 'bolted, bare, vacuum')
network.addRadiation('bulkhead', 'sink', emissivity = 0.85, area = 0.9)

schedule = {'skin': lambda t: 4000.0 if t <= 140.0 else 0.0}

result = network.solveTransient(heatLoadSchedule = schedule)
print(result['truncated'], result['stillRising'])

soakback = network.findSoakback(eventEndTime = 140.0)
for name, entry in soakback['nodes'].items():
    print(name, entry['peakTime'], entry['soaksBack'])

print(network.checkLumpedCapacitance('bulkhead', coefficient = 50.0,
                                     characteristicLength = 0.01, conductivity = 167.0))
print(network.resistanceSensitivity()['shares'])
```

---

## References

- Gilmore, *Spacecraft Thermal Control Handbook*, volume I, chapter 15
- Patankar, *Numerical Heat Transfer and Fluid Flow*
- ECSS-E-ST-31-04C, *Thermal analysis*
- NASA-STD-7009, *Models and simulations*
- Incropera and DeWitt, finite difference formulation
