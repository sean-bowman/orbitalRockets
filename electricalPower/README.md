# electricalPower

**Electrical Power, Distribution and Harnessing**

> **Status: complete.** Four classes, twelve documents and 61 tests, with a worked example that finds four results each the opposite of the obvious one.

---

## What This Is

The electrical system is the one that touches every other subsystem, and harnessing is reliably underestimated in both mass and schedule. This domain covers power generation and storage, distribution and protection, harness design, and the grounding and bonding scheme that determines whether the vehicle has an EMI problem.

It is included because a fluid system with valves and instrumentation is an electrical system too, and the failure modes are shared.

**Most of this domain's inputs are somebody else's outputs.** A heater duty cycle is a thermal design, a bus voltage is an architecture decision, and the firing circuit belongs to mechanisms. That is the shape of the domain and it explains why so much of the work here is bookkeeping and boundary-drawing.

---

## The four results

**Voltage drop chooses the wire gauge, not current.** Ampacity says 20 AWG and voltage drop says 14: six gauge steps and four times the copper. A harness sized on current would leave a 28 V load at 25.1 V and would not function. The reason is geometry rather than electricity, because a launch vehicle harness is long relative to its currents.

**The load that dominates is not the one anybody worries about.** The propellant heaters get the attention and avionics consumes twice their energy, because a 35 W load at full duty beats a 42 W load that cycles. **The heater is still the number worth checking**: sweeping its duty cycle moves the mission energy by 44 per cent, on a load that is 24 per cent of it. The ranking by energy and the ranking by uncertainty are different lists.

**The battery nameplate is 1.85 times the energy delivered**, before any margin, because depth of discharge and cold multiply. Neither is a margin. And the lightest chemistry on the list cannot do the job: lithium thionyl chloride has two and a half times the specific energy and a rate limit thirty times too low, so **the discharge rate decides the chemistry and nothing else in the calculation does.**

**Peak and hold returns three quarters of the valve power** for a resistor and a transistor, because power goes as the square of current. And the hot coil is the design case: a coil at 100 C makes 42 per cent less force than at 20.

---

## Design Ethos

- Harness mass is always more than estimated. Estimate it from connector and run counts, not from a fraction.
- Grounding is a topology decision made early and expensive to change late.
- Every connector is a failure point, and connector count is the best available reliability proxy.
- Voltage drop over a long run is a real constraint, not a rounding error.
- Batteries are a thermal problem and a safety problem before they are an energy problem.

---

## Documentation

| Document | Covers | Status |
|---|---|---|
| [PowerOverview.md](docs/PowerOverview.md) | Hub: what the domain found, the architecture decisions, document index | **written** |
| [BatteriesAndStorage.md](docs/BatteriesAndStorage.md) | The two derations, rate against energy, chemistries, safety | **written** |
| [PowerDistribution.md](docs/PowerDistribution.md) | Bus voltage, topology, switching, protection, what happens on a short | **written** |
| [HarnessDesign.md](docs/HarnessDesign.md) | The AWG definition, the two constraints, mass counted rather than fractioned | **written** |
| [GroundingAndBonding.md](docs/GroundingAndBonding.md) | Single point against multipoint, structure as return, bonding | **written** |
| [EMIAndEMC.md](docs/EMIAndEMC.md) | Four problems with one name, the three mitigations, what a test catches | **written** |
| [PyroCircuits.md](docs/PyroCircuits.md) | Where the firing circuit lives, and what it imposes back on this domain | **written** |
| [ValveAndActuatorDrive.md](docs/ValveAndActuatorDrive.md) | Peak and hold, the hot coil, inrush, flyback | **written** |
| [PowerQuality.md](docs/PowerQuality.md) | The four disturbances, brownout, and the restart problem | **written** |
| [ElectricalTesting.md](docs/ElectricalTesting.md) | Continuity, insulation, hipot, and why the order matters | **written** |
| [StandardsIndex.md](docs/StandardsIndex.md) | One exact definition and five unread standards | **written** |
| [ValidationReferences.md](docs/ValidationReferences.md) | The tightest anchor in the repository, and three gaps | **written** |

## Library

| Class | Computes | Status |
|---|---|---|
| `PowerBudget` | Load rollup by phase, peak and energy separately, drivers, duty cycle sensitivity | **written** |
| `Battery` | Derating, pack sizing, discharge rate check, chemistry comparison | **written** |
| `HarnessSizing` | Gauge from both constraints, derating, mass counted, bus voltage trade | **written** |
| `SolenoidDrive` | Pull-in and hold, hot coil, inrush, flyback and the closing time it sets | **written** |
| `PyroCircuit` | Firing current, no-fire margin, stray current | **not built** |

**`PyroCircuit` was deliberately not built.** `PyrotechnicInitiator` in [mechanismsAndSeparation](../mechanismsAndSeparation/) already computes the firing current, the no-fire margin and the parallel-device arithmetic. This domain supplies the bus voltage and the harness resistance; that one decides whether the device fires. See [PyroCircuits](docs/PyroCircuits.md).

**`SolenoidDrive` was added beyond the plan**, because the objectives asked for inrush, holding and flyback and all three are computable.

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../common/](../common/) through this domain's `powerUtils.py`.

---

## Worked example

`codeInterface.py` sizes an upper stage electrical system.

| Question | Answer |
|---|---|
| What drives the mission energy | avionics |
| What drives the peak power | thrust vector actuators |
| What drives the uncertainty | propellant heaters |
| Heater duty cycle swing on mission energy | 44 % |
| Battery nameplate over energy delivered | 1.85x |
| Gauge from ampacity | 20 AWG |
| Gauge from voltage drop | **14 AWG** |
| Harness mass, counted | 8.12 kg |
| Peak and hold saving per valve | 75 % |

```bash
python electricalPower/codeInterface.py
```

---

## The anchor, and the gaps

This domain has **the tightest single validation anchor in the repository and the longest list of unread standards**, and the two do not overlap.

The AWG definition is exact: computed conductor resistances reproduce published tables to four significant figures. That is the half of the gauge comparison the central result rests on.

Against that, SAE AS50881, MIL-STD-461, MIL-STD-464, MIL-STD-704 and MIL-STD-1576 were all not read, so ampacity, emissions limits and power quality tolerances are representative. **A cell datasheet for the actual battery would close three of the five modelling gaps** and is more tractable than any of the standards.

See [ValidationReferences](docs/ValidationReferences.md), which states this at the top rather than at the bottom.

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [fluidSystems](../fluidSystems/) | Valve actuation, heaters and instrumentation are all electrical loads |
| [mechanismsAndSeparation](../mechanismsAndSeparation/) | Owns the firing circuit; this domain supplies its bus and harness resistance |
| [thermalManagement](../thermalManagement/) | Heater power is the largest steady load on a storable-propellant vehicle, and its duty cycle is a thermal output |
| [avionicsAndGNC](../avionicsAndGNC/) | Shares the harness, the grounding scheme and the EMI environment |
| [vehicleArchitecture](../vehicleArchitecture/) | Harness and battery mass go into the mass chain, where a kilogram costs eleven at liftoff |

---

Sean Bowman
