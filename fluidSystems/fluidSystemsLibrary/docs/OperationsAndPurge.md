[Home](../../README.md) > Operations, Purge and Inerting

# Operations, Purge and Inerting

## Contents

- [Overview](#overview)
- [Purge and inerting](#purge-and-inerting)
- [Loading and detanking](#loading-and-detanking)
- [Safing](#safing)
- [Lockout and hazardous operations](#lockout-and-hazardous-operations)
- [Ground support equipment](#ground-support-equipment)
- [Sequences and interlocks](#sequences-and-interlocks)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A fluid system spends almost all of its life in an operational state rather than a design state, and most of the accidents happen during operations rather than during firing. The design decisions that matter operationally are made early and are expensive to change later:

- Can every volume be purged and verified?
- Can every volume be drained?
- Can the system be safed without opening a joint?
- Is there a vent path from everywhere to somewhere safe?
- Can a single valve failure trap propellant?

**A system that cannot be safed is a system that cannot be worked on.**

---

## Purge and inerting

**Purging** replaces the contents of a volume with an inert gas. It is done for four reasons:

1. **Before propellant loading**, to remove air and moisture that would react with the propellant
2. **After propellant unloading**, to remove residual propellant before any joint is opened
3. **Continuously during operation**, to keep a hazardous atmosphere out of a cavity
4. **Before welding**, to prevent root oxidation. See [Welds.md](Welds.md)

### Purge methods

| Method | How it works | Effectiveness | Time |
|---|---|---|---|
| **Flow-through** | Continuously flow purge gas through the volume | Depends on flow path and dead legs | Long |
| **Pressure-vacuum cycling** | Evacuate, backfill with inert gas, repeat | **Excellent.** Each cycle divides the residual by the pressure ratio | Medium |
| **Pressure cycling (no vacuum)** | Pressurize with inert gas, vent, repeat | Good. Each cycle divides by the pressure ratio | Medium |
| **Dilution (single fill)** | Fill and hold | Poor. Only mixes | Fast |

**Pressure cycling is the method to use and the arithmetic is simple.** Each cycle from `P_high` down to `P_low` reduces the residual contaminant fraction by `P_low / P_high`:

```
residual fraction after n cycles = (P_low / P_high)^n
```

Cycling between 1 MPa and 100 kPa (a 10:1 ratio) reduces the residual by a factor of 10 per cycle. Six cycles reaches one part per million. **That is far faster and far more reliable than flowing purge gas for an hour**, because it does not depend on the flow reaching every corner.

**Flow-through purging is defeated by dead legs.** A branch off the main flow path exchanges its contents only by diffusion, which is orders of magnitude slower than the bulk flow. A flow-through purge of a system with dead legs will show a clean reading at the vent and leave the dead legs full. This is a specific and repeated cause of exposure incidents when a joint is subsequently opened.

### Verification

**Purge is verified by measurement, not by time.** The time to purge depends on the geometry, the flow rate and the dead legs, none of which are reliably known.

| Contaminant | Verification | Typical requirement |
|---|---|---|
| Oxygen (before fuel loading) | Oxygen analyser at the vent | < 1 % for flammability, < 0.1 % for hydrogen |
| Moisture | Dew point meter | -40 degC to -70 degC dew point |
| Hydrazine vapor | Instrumental vapor monitor | Below the TLV, 0.01 ppm |
| Hydrocarbon | Combustible gas detector | < 10 % of LFL |
| Inert gas (before entry) | Oxygen analyser | **> 19.5 % oxygen before any human entry** |

**Sample from the far end of the purge path**, not from the inlet. A sample taken near the purge inlet reads the purge gas.

### Purge gas

**Nitrogen** for general inerting. Cheap, available, and it will not support combustion.

**Helium** where nitrogen is unsuitable: cryogenic systems below 130 K (nitrogen condenses), and anywhere a subsequent helium leak check will be performed.

**Never air.** Shop air carries compressor oil and water, both of which are contaminants and one of which is an ignition source in oxygen.

**Purge gas quality is a specification**: filtered to the system cleanliness level, dried to a specified dew point, from a verified source. A purge with dirty gas contaminates the system it was supposed to clean.

---

## Loading and detanking

**Loading sequence, generically:**

1. Verify the system is clean, leak checked and configured
2. Purge and verify (oxygen and moisture)
3. Chill down if cryogenic. See [CryogenicSystems.md](CryogenicSystems.md)
4. Load slowly, monitoring level, temperature and pressure
5. Top off as needed for a cryogen (boil-off continues)
6. Isolate, verify isolation, pressurize
7. Verify the pressurization and the relief protection

**Detanking (unloading):**

1. Depressurize slowly. See the explosive decompression note in [Seals.md](Seals.md)
2. Drain to a receiving vessel through a defined path
3. Purge and verify
4. Only then break a joint

**Both directions are hazardous operations** and both are done to a written, reviewed procedure with the area cleared to the appropriate distance.

**Slow depressurization** matters for three reasons: explosive decompression of seals, thermal effects (a rapidly depressurizing gas cools and can freeze moisture or embrittle a component), and the fact that a fast depressurization is itself a transient that can generate a surge.

**A cryogenic system cannot simply be "drained".** The residual liquid boils, the vapor has to go somewhere, and the hardware is still cold enough to condense air on it for a long time after the liquid is gone.

---

## Safing

Safing means putting the system into a state where it cannot release energy. It is a defined configuration, not a vague intention.

**Safe configuration typically means:**

| Item | Safe state |
|---|---|
| Propellant | Drained, purged, verified |
| Pressurant | Vented, verified at ambient |
| Pressurized volumes | Vented, with the vent path verified open |
| Valves | In a defined and verified position, locked |
| Electrical | Power removed, ordnance disconnected and shorted |
| Ordnance | Safed per its own procedure |

**Two-fault tolerance** is the usual requirement for a hazardous operation: no single failure, and no credible combination of two failures, may result in a hazardous condition. In practice that means redundant isolation (two valves in series), independent verification, and physical locks rather than electrical inhibits alone.

**Verify the vent path is open.** A vented system with a blocked vent is a pressurized system that believes it is safe. Ice in a cryogenic vent line is the classic case.

**Spacecraft end-of-life passivation** is a distinct requirement covered in [Passivation.md](Passivation.md): every pressurized volume must be vented at end of mission per NASA-STD-8719.14, which means the design has to include a way to do it.

---

## Lockout and hazardous operations

**Before any joint is broken:**

1. Verify the system is drained
2. Verify it is purged, by measurement
3. Verify it is depressurized, by an independent gauge (not by the control system)
4. Lock out and tag the isolation valves and the power
5. Verify the lockout, physically

**"I depressurized it" is not verification.** The single most common route to a personnel injury in fluid system work is a joint broken on a system that someone believed was safe. Independent physical verification at the joint is the control.

**Residual propellant is the specific hazard for hydrazine and hypergolics.** A line that has been drained still has a film on the wall, and that film has a vapor pressure. The purge exists to remove it and the verification exists to prove the purge worked. See [Hydrazine.md](Hydrazine.md).

**Personal protective equipment** is selected for the credible exposure, not the expected one. For hydrazine transfer that means SCAPE or equivalent with supplied air. See [Hydrazine.md](Hydrazine.md).

**Confined space entry** into any volume that has contained an inert gas requires oxygen verification above 19.5 percent, continuous monitoring, an attendant and a retrieval plan. **Nitrogen asphyxiation gives no warning**: it is odourless and the body does not sense oxygen deficiency, only carbon dioxide excess.

---

## Ground support equipment

GSE is a fluid system too, and it is subject to the same design rules with three differences:

1. **It is reconfigured constantly**, so every joint is made and broken many times. That argues for quick disconnects and against permanent joints, at the cost of leak rate.
2. **It is heavier and cheaper**, so mass-driven decisions reverse: nitrogen instead of helium, thicker walls, larger lines.
3. **It contains the hazard**, so its relief protection and its containment matter more than the flight system's in many cases.

**Interface control** between GSE and flight hardware is where problems concentrate. The umbilical disconnect has to separate reliably at pressure, seal on both sides, and not damage the flight interface. Verify the separation force at pressure: a quick disconnect that will not separate under residual pressure is a launch hold.

**GSE cleanliness must match or exceed the flight system's.** A clean flight system loaded through dirty GSE is a dirty flight system.

---

## Sequences and interlocks

**Valve sequencing** is where operational logic meets fluid physics:

- **Never close two valves in series simultaneously** on a liquid line. The volume between them is trapped, and thermal expansion has nowhere to go. Sequence the closures and provide a relief path.
- **Open slowly into a dead-ended volume**, particularly in oxygen. See [WaterHammer.md](WaterHammer.md).
- **Vent before isolating**, not after.
- **Verify each step before commanding the next** where the consequence of an out-of-sequence command is hazardous.

**Interlocks** enforce sequence in hardware or software. The design question is what happens when an interlock is bypassed, because it will be bypassed at some point during troubleshooting. An interlock that can be bypassed silently is an interlock that will be.

**Abort and safe-state logic.** For every automated sequence, define what happens on a loss of command, a loss of power, and a loss of pneumatic supply. Each valve's fail state (open, closed, as-is) is a design decision that must be made deliberately and verified by test.

---

## Design rules of thumb

| Rule | Value | Why |
|---|---|---|
| Purge by pressure cycling | 10:1 ratio, 5 to 6 cycles | 1 ppm residual; far better than flow-through |
| Verify purge by measurement | Always, at the far end | Time-based purging does not account for dead legs |
| Eliminate dead legs | Length < 3 diameters | Diffusion-limited purging leaves them full |
| Purge gas | Filtered, dried, never shop air | It contaminates what it was cleaning |
| Helium purge below 130 K | Nitrogen condenses | |
| Every isolatable volume gets a relief path | Absolute | Trapped liquid, especially cryogen |
| Never close two series valves simultaneously | Sequence them | Trapped volume |
| Independent verification before breaking a joint | Always | The most common injury mechanism |
| Oxygen > 19.5 % before entry | Absolute | Nitrogen asphyxiation gives no warning |
| Two-fault tolerance for hazardous operations | Requirement | Redundant isolation plus physical locks |
| Verify vent path open when safing | Always | A blocked vent means it is not safed |
| Verify QD separation force at pressure | Always | A stuck QD is a launch hold |
| GSE cleanliness >= flight cleanliness | Always | The system is only as clean as what fills it |

---

## Failure modes

**Joint broken on a system that was not actually purged.** Personnel exposure. The dominant injury mechanism in propellant work.

**Dead leg holding propellant through a flow-through purge.** The vent reads clean and the dead leg is full.

**Trapped volume between two simultaneously closed valves.** Thermal expansion bursts the line. With a cryogen the expansion ratio is several hundred to one.

**Blocked vent on a "safed" system.** Ice, contamination or a closed valve. The system is pressurized and believed safe.

**Nitrogen asphyxiation.** In a confined space, with no warning.

**Adiabatic compression ignition on valve opening.** In an oxygen system, opening fast into a dead end. See [WaterHammer.md](WaterHammer.md).

**Quick disconnect that will not separate at pressure.** A launch hold, or a damaged flight interface if it is forced.

**Interlock bypassed during troubleshooting and not restored.** The interlock existed for a reason and the reason is still there.

**Contamination introduced by GSE.** A clean flight system loaded through a dirty ground system.

**Loading into an unverified configuration.** A valve in the wrong position, a blank left installed, a line not reconnected after a modification.

---

## Standards

| Standard | Scope |
|---|---|
| **AFSPCMAN 91-710** | Range safety user requirements. The governing document for US range operations |
| **NASA-STD-8719.12** | Safety standard for explosives, propellants and pyrotechnics |
| **NASA-STD-8719.17** | Requirements for ground-based pressure vessels and pressurized systems |
| MIL-STD-1522 | Safe design and operation of pressurized missile and space systems |
| KSC-STD-Z-0005 | Design and operation of hazardous propellant facilities |
| NFPA 55 | Compressed gases and cryogenic fluids code |
| CGA P-12 | Safe handling of cryogenic liquids |
| CGA G-4.4 | Oxygen pipeline and piping systems |
| OSHA 29 CFR 1910.146 | Permit-required confined spaces |
| OSHA 29 CFR 1910.147 | Control of hazardous energy (lockout/tagout) |
| ANSI/AIAA G-095 | Guide to safety of hydrogen and hydrogen systems |
| **NASA-STD-8719.14** | Process for limiting orbital debris (end-of-life passivation) |

---

## Tool interface

Operational analysis draws on several classes:

```python
from LeakPath import LeakPath
from WaterHammer import WaterHammer
from Pressurization import Pressurization

# Hazard-derived allowable leak rate: what the purge and leak check must achieve
leak = LeakPath()
leak.setInputs({'species': 'He', 'upstreamPressure': 2.4e6, 'temperature': 293.15})
allowable = leak.calculateAllowableFromHazard(
    enclosureVolume    = 30.0,      # the bay the leak discharges into [m^3]
    concentrationLimit = 1e-8,      # hydrazine TLV, 0.01 ppm
    ventilationRate    = 0.0,       # unventilated case governs the safety argument
    exposureTime       = 28800.0)   # an 8 hour shift
print(allowable['allowableUnventilatedSccs'])

# Adiabatic compression check for an oxygen valve opening sequence
surge = WaterHammer()
surge.setInputs({'fluid': 'Water', 'pressure': 1.0e5, 'temperature': 293.15,
                 'velocity': 0.1, 'innerDiameter': 0.01, 'wallThickness': 0.001,
                 'length': 1.0})
compression = surge.calculateAdiabaticCompression(101325.0, 20e6, gamma = 1.4)
print(compression['finalTemperature'], compression['materialsAtRisk'])
```

The purge cycle arithmetic is simple enough that it does not warrant a class: the residual fraction after `n` cycles between `P_low` and `P_high` is `(P_low / P_high)^n`.

---

## References

1. AFSPCMAN 91-710, *Range Safety User Requirements*.
2. NASA-STD-8719.12B, *Safety Standard for Explosives, Propellants, and Pyrotechnics*.
3. NASA-STD-8719.17B, *NASA Requirements for Ground-Based Pressure Vessels and Pressurized Systems*.
4. CGA P-12, *Safe Handling of Cryogenic Liquids*.
5. ANSI/AIAA G-095A-2017, *Guide to Safety of Hydrogen and Hydrogen Systems*.
6. AFRPL-TR-69-149, *Hydrazine Handling Manual*.
7. Schmidt, E. W., *Hydrazine and Its Derivatives*, 2nd ed., Wiley, 2001.
8. NASA-STD-8719.14C, *Process for Limiting Orbital Debris*.
