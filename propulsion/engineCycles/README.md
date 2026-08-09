# engineCycles

**Cycle Selection and Power Balance**

> **Status: complete.** Two classes, seven documents and 67 tests, with a worked example that finds three of four candidate cycles eliminated by arithmetic before any performance number is compared. Validated at hardware level against the RS-25 pressure ladder and the RL10 expander ceiling.

---

## What This Is

The first decision made about an engine and the one that constrains everything after it. The cycle determines whether there is a turbopump at all, what the turbine drive gas is, whether any propellant is discarded, and what chamber pressure is reachable.

The power balance is what makes a cycle real. Turbine power must equal pump power, the turbine drive gas has to come from somewhere at a pressure and temperature that closes, and a cycle that does not close is not a design choice, it is arithmetic.

Reference documentation, a component class library and a tiered test suite, matching the [fluidSystems](../../fluidSystems/) template.

---

## Documentation

| Document | Covers | Status |
|---|---|---|
| [CycleSelection.md](docs/CycleSelection.md) | One question decides everything, and most candidates are eliminated rather than chosen | **written** |
| [PowerBalance.md](docs/PowerBalance.md) | Turbine power equals pump power, and the expansion term that separates the cycles | **written** |
| [GasGeneratorCycle.md](docs/GasGeneratorCycle.md) | The dump penalty, and why it is invisible to a thrust chamber model | **written** |
| [StagedCombustion.md](docs/StagedCombustion.md) | The pressure ladder, fuel rich against oxidiser rich, and full flow | **written** |
| [ExpanderCycle.md](docs/ExpanderCycle.md) | The heat balance ceiling, why it exists, and why RL10 sits at it | **written** |
| [PressureFedSystems.md](docs/PressureFedSystems.md) | The tank as the pump, and the factor of forty eight | **written** |
| [ValidationReferences.md](docs/ValidationReferences.md) | The external sources the tools are checked against, and what is not checked | **written** |

## Library

| Class | Computes | Status |
|---|---|---|
| `EngineCycle` | The pressure ladder, the discarded flow, and the impulse each cycle delivers | **written** |
| `PowerBalance` | Turbine and pump matching, the driving flow, and whether the cycle closes | **written** |

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../../common/](../../common/) through this sub-domain's `cycleUtils.py`.

---


## Worked example

`codeInterface.py` asks which cycle the hub's 100 kN booster should use.

| Cycle | Verdict | Decided by |
|---|---|---|
| Pressure fed | **Eliminated** | Tank mass: 2219 kg of pressure vessel against 46 kg pumped |
| Expander | **Eliminated** | Heat balance: ceiling near 4 MPa against a 10 MPa chamber |
| Staged combustion | Admitted | Costs pump discharge, 2.20 x chamber pressure |
| Gas generator | Admitted | Costs impulse, 2.5 per cent |

Only the last two are a trade. The expander ceiling falls between 4.0 and 4.5 MPa, and RL10 runs at 4.4.

```bash
python propulsion/engineCycles/codeInterface.py
```

---

## Where this sub-domain connects

| Domain | Interaction |
|---|---|
| [../turbomachinery/](../turbomachinery/) | The power balance sizes the pumps and the turbine |
| [../combustionDevices/](../combustionDevices/) | Preburners and gas generators are combustion devices |
| [../../vehicleArchitecture/](../../vehicleArchitecture/) | Cycle choice sets engine Isp and mass, which sets the vehicle |

---

Sean Bowman
