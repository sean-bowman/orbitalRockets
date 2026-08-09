# turbomachinery

**Pumps, Turbines and Shaft Systems**

> **Status: complete.** Three classes, seven documents and 63 tests, with a worked example that finds the optimum shaft speed moves by a factor of two depending on the engine cycle. Validated at hardware level against the RS-25 turbopumps: 9 per cent on shaft power at the published stage count.

---

## What This Is

What makes a pump-fed engine possible, and the single most expensive component to develop. A turbopump is a high speed machine handling a cryogenic liquid at one end and hot gas at the other, on a common shaft, with a seal package between them that has to keep the two apart.

Cavitation is the constraint that shapes the inlet. A pump with inadequate net positive suction head does not degrade gracefully; it breaks down, and the inducer exists solely to let the main impeller run at a speed the tank pressure could not otherwise support.

Reference documentation, a component class library and a tiered test suite, matching the [fluidSystems](../../fluidSystems/) template.

---

## Documentation

| Document | Covers | Status |
|---|---|---|
| [PumpSizing.md](docs/PumpSizing.md) | Specific speed, staging, tip speed limits, efficiency, and the RS-25 check | **written** |
| [CavitationAndNPSH.md](docs/CavitationAndNPSH.md) | Suction specific speed, the four thirds power, and the chain to tank mass | **written** |
| [TurbineSizing.md](docs/TurbineSizing.md) | Spouting velocity, the classical impulse optimum, and why a rocket never reaches it | **written** |
| [ShaftDynamics.md](docs/ShaftDynamics.md) | Critical speeds, whirl, bearings, and why there is no class for this | **written** |
| [SealsAndInterpropellantSeals.md](docs/SealsAndInterpropellantSeals.md) | The seal sequence, purge, and why seals decide rotordynamics | **written** |
| [TurbopumpIntegration.md](docs/TurbopumpIntegration.md) | One shaft or two, the cycle that sets the speed, boost pumps, the start problem | **written** |
| [ValidationReferences.md](docs/ValidationReferences.md) | The external sources the tools are checked against, and what is not checked | **written** |

## Library

| Class | Computes | Status |
|---|---|---|
| `Pump` | Specific speed, staging, impeller sizing, efficiency, power, bearing DN | **written** |
| `Inducer` | Suction specific speed, NPSH both directions, the tank pressure it demands | **written** |
| `Turbine` | Spouting velocity, blade speed ratio, efficiency, driving flow, limits | **written** |
| `ShaftSystem` | Critical speeds, bearing loads and life | **not built, see below** |

**`ShaftSystem` was planned and is not built.** The shaft speed constraint it existed to carry turned out to belong in the three classes that already own the physics: the bearing DN limit sits in `Pump.sizeImpeller` because it follows from the impeller diameter, and the cavitation ceiling sits in `Inducer.maximumShaftSpeed`. What is left is critical speed and bearing life, and bearing life needs manufacturer load-rating data this repository does not have. A class that computed a critical speed from an assumed shaft stiffness would be inventing the input that decides the answer.

The shaft speed reconciliation across all three constraints is a system result and it belongs in the worked example rather than in a class.

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../../common/](../../common/) through this sub-domain's `turbomachineryUtils.py`.

---


## Worked example

`codeInterface.py` reconciles four constraints on one shaft and finds the answer is decided by something none of them owns.

| Cycle | Optimum shaft speed | What dominates |
|---|---|---|
| Open, gas generator | **55 000 rpm** | Dumped turbine propellant |
| Closed, staged combustion | **27 000 rpm** | Tank pressure |

A factor of 2.04, with nothing about the pumps changing between the two. The cycle is chosen in [engineCycles](../engineCycles/) before any of this, and it is not usually thought of as a turbopump decision.

```bash
python propulsion/turbomachinery/codeInterface.py
```

---

## Where this sub-domain connects

| Domain | Interaction |
|---|---|
| [../engineCycles/](../engineCycles/) | The power balance is what sizes the turbine |
| [../../fluidSystems/](../../fluidSystems/) | Tank pressure and feed line losses set the available NPSH |
| [../../aerospaceMaterials/](../../aerospaceMaterials/) | Superalloy turbine hardware, and hydrogen embrittlement in the fuel pump |
| [../../aerospaceStructures/](../../aerospaceStructures/) | Shaft dynamics, and the pump as a mounted mass |

---

Sean Bowman
