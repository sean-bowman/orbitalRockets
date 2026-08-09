# turbomachinery

**Pumps, Turbines and Shaft Systems**

> **Status: scaffolded.** The topic coverage below is defined and the documents are planned. Nothing in this sub-domain is written yet. See [../../fluidSystems/](../../fluidSystems/) for a completed domain.

---

## What This Is

What makes a pump-fed engine possible, and the single most expensive component to develop. A turbopump is a high speed machine handling a cryogenic liquid at one end and hot gas at the other, on a common shaft, with a seal package between them that has to keep the two apart.

Cavitation is the constraint that shapes the inlet. A pump with inadequate net positive suction head does not degrade gracefully; it breaks down, and the inducer exists solely to let the main impeller run at a speed the tank pressure could not otherwise support.

Reference documentation, a component class library and a tiered test suite, matching the [fluidSystems](../../fluidSystems/) template.

---

## Planned documentation

| Document | Covers | Status |
|---|---|---|
| `docs/PumpSizing.md` | Specific speed, head and flow, impeller geometry, and the efficiency you can expect | planned |
| `docs/CavitationAndNPSH.md` | Suction specific speed, the inducer, and why tank pressure is a pump requirement | planned |
| `docs/TurbineSizing.md` | Impulse and reaction, admission, blade speed ratio, and the thermal problem | planned |
| `docs/ShaftDynamics.md` | Critical speeds, bearings, and the rotordynamic margin | planned |
| `docs/SealsAndInterpropellantSeals.md` | The seal package, purges, and keeping oxidiser away from fuel | planned |
| `docs/TurbopumpIntegration.md` | Layout, common shaft against separate, gearing, and the start problem | planned |

## Planned library

| Class | Computes | Status |
|---|---|---|
| `Pump` | Specific speed, head rise, impeller sizing, efficiency and power | planned |
| `Inducer` | Suction specific speed, NPSH required, and the cavitation margin | planned |
| `Turbine` | Blade speed ratio, admission, stage sizing, power and inlet temperature | planned |
| `ShaftSystem` | Critical speeds, bearing loads and life, and the rotordynamic check | **not built, see below** |

**`ShaftSystem` was planned and is not built.** The shaft speed constraint it existed to carry turned out to belong in the three classes that already own the physics: the bearing DN limit sits in `Pump.sizeImpeller` because it follows from the impeller diameter, and the cavitation ceiling sits in `Inducer.maximumShaftSpeed`. What is left is critical speed and bearing life, and bearing life needs manufacturer load-rating data this repository does not have. A class that computed a critical speed from an assumed shaft stiffness would be inventing the input that decides the answer.

The shaft speed reconciliation across all three constraints is a system result and it belongs in the worked example rather than in a class.

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../../common/](../../common/) through this sub-domain's `turbomachineryUtils.py`.

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
