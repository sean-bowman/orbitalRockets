# engineCycles

**Cycle Selection and Power Balance**

> **Status: scaffolded.** The topic coverage below is defined and the documents are planned. Nothing in this sub-domain is written yet. See [../../fluidSystems/](../../fluidSystems/) for a completed domain.

---

## What This Is

The first decision made about an engine and the one that constrains everything after it. The cycle determines whether there is a turbopump at all, what the turbine drive gas is, whether any propellant is discarded, and what chamber pressure is reachable.

The power balance is what makes a cycle real. Turbine power must equal pump power, the turbine drive gas has to come from somewhere at a pressure and temperature that closes, and a cycle that does not close is not a design choice, it is arithmetic.

Reference documentation, a component class library and a tiered test suite, matching the [fluidSystems](../../fluidSystems/) template.

---

## Planned documentation

| Document | Covers | Status |
|---|---|---|
| `docs/CycleSelection.md` | The cycles, their honest trades, and what each one is actually for | planned |
| `docs/PowerBalance.md` | Turbine power equals pump power, and what makes a cycle close or not | planned |
| `docs/GasGeneratorCycle.md` | Open cycle, the turbine exhaust penalty, and why it persists | planned |
| `docs/StagedCombustion.md` | Oxidiser rich, fuel rich, and full flow. The pressure ladder | planned |
| `docs/ExpanderCycle.md` | The heat transfer limit, and why there is a thrust ceiling | planned |
| `docs/PressureFedSystems.md` | No turbomachinery, and the tank mass that pays for it | planned |

## Planned library

| Class | Computes | Status |
|---|---|---|
| `EngineCycle` | Cycle definition, the pressure ladder, and the discarded flow fraction | planned |
| `PowerBalance` | Turbine and pump power matching, drive gas conditions, closure check | planned |

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../../common/](../../common/) through this sub-domain's `cycleUtils.py`.

---

## Where this sub-domain connects

| Domain | Interaction |
|---|---|
| [../turbomachinery/](../turbomachinery/) | The power balance sizes the pumps and the turbine |
| [../combustionDevices/](../combustionDevices/) | Preburners and gas generators are combustion devices |
| [../../vehicleArchitecture/](../../vehicleArchitecture/) | Cycle choice sets engine Isp and mass, which sets the vehicle |

---

Sean Bowman
