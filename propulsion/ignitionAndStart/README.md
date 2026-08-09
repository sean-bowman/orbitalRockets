# ignitionAndStart

**Ignition, Start and Shutdown Transients**

> **Status: complete.** Four classes, six documents and 63 tests, with a worked example that finds the start sequence exists to control accumulation rather than to give the igniter time. Two of the four planned classes were built as planned and two more were added.

---

## What This Is

The few hundred milliseconds at each end of a burn, which is where a disproportionate share of engine failures live. An engine that runs happily at steady state can destroy itself during a start that admits propellant in the wrong order.

Shutdown is harder than start and gets less attention. At start the engine is cold and empty; at shutdown it is hot, full, and the propellants continue to arrive after the valves are commanded closed.

Reference documentation, a component class library and a tiered test suite, matching the [fluidSystems](../../fluidSystems/) template.

**This is the least externally anchored sub-domain in the propulsion tree.** One source carries almost all of its validation, four of its calculations are registered as unvalidated, and its defensible claims are rankings rather than magnitudes. [ValidationReferences](docs/ValidationReferences.md) says so at the top rather than at the bottom.

---

## The result

The chamber that [combustionDevices](../combustionDevices/) sized holds its combustion gas for **1.47 ms**. Admitting mainstage flow while the engine lights gives a **2.9 ms** window before two chamber-fulls have accumulated, and no detection system acts in 2.9 ms.

So the sequence cannot rely on detecting ignition. It has to make the accumulation small by admitting almost none of the flow.

| Ignition delay | Flow the sequence may admit |
|---|---|
| Hypergolic slug, 3 ms | 98 % |
| Spark, prompt, 20 ms | 15 % |
| Spark, cold, 50 ms | 6 % |

**That is what a TEA-TEB cartridge actually buys: not reliability and not energy, but permission to skip the slow part of the sequence.** It is also why the RS-25 takes 1.5 seconds to prime its main chamber and 5 seconds to reach rated power.

---

## Documentation

| Document | Covers | Status |
|---|---|---|
| [StartTransient.md](docs/StartTransient.md) | The accumulation ratio, priming, and the published RS-25 sequence | **written** |
| [IgnitionSystems.md](docs/IgnitionSystems.md) | The five types, what decides the selection, and the detection window | **written** |
| [ShutdownTransient.md](docs/ShutdownTransient.md) | Decay rates owned by the vehicle, residual impulse, and why fuel-rich | **written** |
| [ChillInAndConditioning.md](docs/ChillInAndConditioning.md) | The enthalpy balance, the band, and why hydrogen is a different problem | **written** |
| [RestartAndReuse.md](docs/RestartAndReuse.md) | What restart demands, and why it is a tank requirement first | **written** |
| [ValidationReferences.md](docs/ValidationReferences.md) | The one hardware source, and the four things it cannot check | **written** |

## Library

| Class | Computes | Status |
|---|---|---|
| `StartTransient` | Accumulation, the overpressure bound, priming, sequence ordering | **written** |
| `IgnitionSystem` | Igniter selection with an audit trail, and the detection window | **written** |
| `ShutdownTransient` | Decay limits, residual impulse and its scatter, shutdown ordering | **written** |
| `ChillDown` | Conditioning propellant, bounded above and below by the two methods | **written** |

**Two classes were added beyond the plan.** `ShutdownTransient` and `ChillDown` cover two of the four objectives, both have real closed-form content, and leaving them out would have meant a sub-domain whose README called shutdown the harder problem while computing nothing about it.

Two of the checks **refuse rather than report**: a start sequence out of order, and a shutdown that would run oxidiser-rich. Both are destroyed engines rather than degraded ones, and nothing in this repository models what happens next.

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../../common/](../../common/) through this sub-domain's `ignitionUtils.py`.

---

## Worked example

`codeInterface.py` takes the 100 kN booster through both transients.

| Question | Answer | Set by |
|---|---|---|
| Chamber residence time | 1.47 ms | Chamber volume and flow |
| Window before two chamber-fulls | 2.9 ms | The same, and the start flow |
| Detection latency needed to act | 10 ms | Physics of the sensor loop |
| Start flow that makes detection work | 29 % | The valve schedule |
| Residual impulse after cutoff | 13.0 kN s | The dribble volume, 88 % of it |
| Of which reaches the trajectory | 1.95 kN s | Its scatter, not its size |
| LOX conditioning band | 1.9 x | The hardware mass |
| LH2 conditioning band | 8.6 x | The chill-down method |

Three of those are set by things not usually described as part of the ignition system: the chamber volume, the valve schedule, and the plumbing downstream of the valves.

```bash
python propulsion/ignitionAndStart/codeInterface.py
```

---

## The margin a start sequence has

The RS-25 primes its three combustors about a tenth of a second apart, and the same source states that a timing error of a tenth of a second can cause significant damage.

**The design spacing and the damaging error are the same number.**

That is why sequences are developed on a test stand rather than on paper, and the same source records what that cost: 19 tests, 23 weeks and 8 turbopump replacements to reach 2 seconds into a 5 second sequence.

---

## Where this sub-domain connects

| Domain | Interaction |
|---|---|
| [../combustionDevices/](../combustionDevices/) | Ignition happens in the chamber, and its residence time is the clock every transient here is measured against |
| [../turbomachinery/](../turbomachinery/) | Pumps have to be conditioned before start and kept fed while they coast down |
| [../../fluidSystems/](../../fluidSystems/) | Valve sequencing, dribble volumes and water hammer at shutdown |
| [../../vehicleArchitecture/](../../vehicleArchitecture/) | Restart is a tank requirement first: settling decides it more often than the igniter does |
| [../../reliabilityAndMissionAssurance/](../../reliabilityAndMissionAssurance/) | Ignition reliability is frequently the driving failure mode |

---

Sean Bowman
