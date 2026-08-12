[Home](../README.md) > Ground Systems Overview

# Ground Systems Overview

## Contents

- [Overview](#overview)
- [What this domain found](#what-this-domain-found)
- [The shape of the domain](#the-shape-of-the-domain)
- [What is computed and what is not](#what-is-computed-and-what-is-not)
- [Document index](#document-index)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [References](#references)

---

## Overview

The vehicle spends hours on the pad and minutes in flight, and most of the risk to people is on the ground. This domain covers the launch site, the ground support equipment, propellant handling, and the operations that connect them.

**Ground systems is a fluid system with different constraints**: heavier, cheaper, reconfigured constantly, and operated by people standing next to it. Most of what a pad needs computing is therefore already computed in [fluidSystems](../../fluidSystems/), which is why this domain builds four classes rather than fifteen.

---

## What this domain found

**A small hydrogen stage is not a small siting problem.** The explosives standard sizes a launch pad from the larger of a sublinear term and a flat fourteen per cent of the propellant mass, and below 84,635 kg the sublinear term governs. A 38 t hydrogen stage comes out at 18.3 per cent and a 4 t one at 38. The effective fraction rises without limit as the load falls, which is the reverse of the intuition it replaces. See [HazardZonesAndSiting](HazardZonesAndSiting.md).

**A launch attempt draws half again the flight load.** Chill-down, boil-off during the fill and replenish during the hold are all spent before liftoff, and on a hydrogen stage the chill-down alone is 35 per cent of the flight load. **A scrub after tanking loses 0.96 flight loads** even with 55 per cent recovered on the detank. See [PropellantStorageAndTransfer](PropellantStorageAndTransfer.md).

**Chill-down rather than fast fill dominates the tanking clock**, at 64 per cent of a 102 minute sequence, because chill-down runs at a fraction of the transfer rate by necessity: the point of it is to boil.

**A hold costs more than its own length.** A hold at T-4 minutes that backs up to T-20 costs 26 minutes against a 10 minute hold, because the re-run is the larger part. See [LaunchOperations](LaunchOperations.md).

**Six launch commit criteria, none worse than 88 per cent alone, give 60.5 per cent together.** Independent conditions multiply, and the 27 point combined penalty is invisible when criteria are reviewed one at a time, which is how they are reviewed. See [WeatherAndConstraints](WeatherAndConstraints.md).

**Attempts beat criteria at every attempt count**, by a factor of 6.9 on a single-attempt campaign. That makes turnaround a launch probability requirement rather than an operational convenience.

**And the campaign in the worked example is propellant limited rather than schedule limited**: the countdown allows eight attempts and the hydrogen storage supports seven. That is a resupply contract rather than an engineering change.

---

## The shape of the domain

Three things about ground systems make it different from every other domain in this repository.

**Most of its inputs are somebody else's outputs.** The chill-down mass comes from propulsion, the boil-off rate from fluid systems, the acoustic environment from environments and loads. What this domain adds is the integration across an operation.

**Most of its content is decisions rather than calculations.** Where the deluge water goes, what the launch commit criteria are, what the abort rules say, who is where during a hazardous operation. Those are written down here because they are decisions, and because writing them down is the only form they take.

**And its one hard standard is about explosives.** [DESR 6055.09](StandardsIndex.md) governs how far away everything has to be, and it was read in full. That is the domain's anchor and it is a strong one.

---

## What is computed and what is not

| Built | Why nothing else does it |
|---|---|
| `HazardSiting` | No other domain converts a propellant load into a distance |
| `PropellantLoading` | Boil-off and chill-down exist elsewhere; nothing adds them up across an attempt |
| `CountdownTimeline` | Nothing else in the repository has a schedule in it |
| `LaunchAvailability` | Nothing else computes a probability of getting off the ground |

| Not built | Where it lives |
|---|---|
| GSE fluid analysis | [fluidSystems](../../fluidSystems/), which computes lines, valves, orifices and reliefs |
| Chill-down mass | [ChillDown](../../propulsion/ignitionAndStart/) in propulsion |
| Boil-off from insulation | [Insulation](../../fluidSystems/) in fluid systems |
| Umbilical retract dynamics | [mechanismsAndSeparation](../../mechanismsAndSeparation/), a spring and a mass |
| Acoustic suppression | [environmentsAndLoads](../../environmentsAndLoads/) owns the acoustic environment |
| Debris footprint | [rangeSafetyAndFTS](../../rangeSafetyAndFTS/) |
| Weather forecasting | Not an engineering calculation at all |

**The reasoning matters more than the verdict in each case**, and it is written into the worked example rather than assumed.

---

## Document index

| Document | Covers |
|---|---|
| [LaunchPadAndFacilities](LaunchPadAndFacilities.md) | Pad layout, flame trench, deluge, lightning, blast |
| [HazardZonesAndSiting](HazardZonesAndSiting.md) | The explosives standard, the hydrogen rule, quantity distance |
| [PropellantStorageAndTransfer](PropellantStorageAndTransfer.md) | Storage, the tanking sequence, ground demand, the scrub cost |
| [UmbilicalsAndDisconnects](UmbilicalsAndDisconnects.md) | Umbilical design, retract, separation, contingency reconnect |
| [GSEDesign](GSEDesign.md) | What ground fluid systems share with flight and where they diverge |
| [LaunchOperations](LaunchOperations.md) | Countdown structure, holds, recycles, turnaround, launch commit |
| [HazardousOperations](HazardousOperations.md) | Loading, clearing, hazard zones, personnel protection |
| [ControlAndDataSystems](ControlAndDataSystems.md) | Ground control architecture, interlocks, command paths, recording |
| [IntegrationAndProcessing](IntegrationAndProcessing.md) | Processing flow, transport, erection, mate |
| [WeatherAndConstraints](WeatherAndConstraints.md) | Weather rules, the multiplication, windows, attempts |
| [StandardsIndex](StandardsIndex.md) | One standard read in full and several not read |
| [ValidationReferences](ValidationReferences.md) | The anchor, what it corrected, and three gaps |

---

## Design rules of thumb

- **Ground systems is a fluid system with different constraints.** Heavier, cheaper, reconfigured constantly.
- **The interface is where the problems are.** Umbilicals and disconnects deserve disproportionate attention.
- **A procedure that cannot be followed under pressure will not be followed under pressure.**
- **Everything that can be verified before the vehicle arrives should be.**
- **Scrub turnaround is a design requirement**, because attempts drive launch probability harder than criteria do.
- **Count the loads in the storage tank**, not the kilograms. A campaign is measured in attempts.

---

## Failure modes

**A siting distance taken from a summary.** The commonly quoted sixty per cent equivalence for hydrogen is a test yield figure, not the siting rule.

**Ground propellant estimated as the flight load.** It is half again as much, and a scrub costs another whole one.

**A hold costed as its own duration.** The re-run is the larger part.

**Turnaround improved anywhere but the governing driver.** It buys nothing.

**Launch commit criteria reviewed one at a time.** They multiply, and the penalty is invisible from inside a single review.

**A campaign planned on schedule alone.** In the worked example the storage tank binds first.

---

## References

- DESR 6055.09, *Defense Explosives Safety Regulation*, Volume 5 Enclosure 4
- NASA-STD-8719.12A, *Safety Standard for Explosives, Propellants and Pyrotechnics*
- [fluidSystems](../../fluidSystems/), which owns the analytical half of ground fluid systems
- [fluidSystemsTesting](../../fluidSystems/fluidSystemsTesting/), because a test stand and a pad share most of their problems
