# groundSystemsAndOperations

**Launch Site, Ground Support Equipment and Operations**

> **Status: complete.** Four classes, thirteen documents and 78 tests, anchored to an explosives siting standard read in full, which corrected two things a summary would have got wrong.

---

## What This Is

The vehicle spends hours on the pad and minutes in flight, and most of the risk to people is on the ground. This domain covers the launch site, the ground support equipment, propellant handling, and the operations that connect them.

**Ground systems is a fluid system with different constraints**: heavier, cheaper, reconfigured constantly, and operated by people standing next to it. Most of what a pad needs computing is therefore already computed in [fluidSystems](../fluidSystems/), which is why this domain builds four classes rather than fifteen and writes down the reasoning for each one it did not build.

---

## The four results

**A small hydrogen stage is not a small siting problem.** The standard sizes a pad from the larger of a sublinear term and a flat fourteen per cent of the propellant mass, and the two are equal at 84,635 kg. Below that the sublinear term governs and the effective fraction rises without limit as the load falls: 18.3 per cent for a 38 t stage, 38 for a 4 t one. That reverses the intuition it replaces, and it means a modest upper stage can drive a pad layout its propellant mass would not suggest.

**A launch attempt draws half again the flight load, and a scrub costs almost another.** Chill-down, boil-off during the fill and replenish during the hold are all spent before liftoff. On the hydrogen stage in the worked example the chill-down alone is 35 per cent of the flight load, one attempt is 1.51 flight loads, and a scrub after tanking loses 0.96 of one even with 55 per cent recovered on the detank. **Chill-down also dominates the tanking clock** at 64 per cent of it, not the fast fill, because chill-down runs at a fraction of the transfer rate by necessity: the point of it is to boil.

**One chain sets the count and one driver sets the turnaround.** The count is 220 minutes against a serial sum of 380. A ten minute hold at T-4 that backs up to T-20 costs 26 minutes, because the re-run is the larger part. The turnaround drivers sum to 94 hours and the turnaround is 48, set entirely by hydrogen resupply, so **fixing it buys 32 hours and no more** because crew duty is waiting at 16.

**Six launch commit criteria at nine tenths each are not nine tenths.** None worse than 88 per cent alone, they give 60.5 per cent together, a combined penalty of 27 points that is invisible when criteria are reviewed one at a time. And **attempts beat criteria at every attempt count**, by a factor of 6.9 on a single-attempt campaign, which makes turnaround a launch probability requirement rather than an operational convenience.

**The campaign closes on the storage tank.** The countdown allows eight attempts in fourteen days and the hydrogen storage supports seven. The binding constraint is a resupply contract, not a countdown and not the weather.

---

## Design Ethos

- Ground systems are a fluid system with different constraints: heavier, cheaper, reconfigured constantly.
- The interface is where the problems are. Umbilicals and disconnects deserve disproportionate attention.
- A procedure that cannot be followed under pressure will not be followed under pressure.
- Everything that can be verified before the vehicle arrives should be.
- Scrub turnaround is a design requirement, not an operational detail, because attempts drive launch probability harder than criteria do.
- Count the loads in the storage tank, not the kilograms. A campaign is measured in attempts.

---

## Documentation

| Document | Covers | Status |
|---|---|---|
| [GroundSystemsOverview.md](docs/GroundSystemsOverview.md) | Hub: what the domain found, the boundaries, document index | **written** |
| [HazardZonesAndSiting.md](docs/HazardZonesAndSiting.md) | The standard, the hydrogen rule, quantity distance, two corrections | **written** |
| [PropellantStorageAndTransfer.md](docs/PropellantStorageAndTransfer.md) | The tanking sequence, ground demand, the scrub cost, storables | **written** |
| [LaunchOperations.md](docs/LaunchOperations.md) | Critical path, holds and recycles, turnaround, launch commit | **written** |
| [WeatherAndConstraints.md](docs/WeatherAndConstraints.md) | Why criteria multiply, why attempts win, correlation, windows | **written** |
| [LaunchPadAndFacilities.md](docs/LaunchPadAndFacilities.md) | Layout from the rings out, deflector, deluge, lightning, hold-down | **written** |
| [UmbilicalsAndDisconnects.md](docs/UmbilicalsAndDisconnects.md) | What crosses, three ways to separate, retract, contingency reconnect | **written** |
| [GSEDesign.md](docs/GSEDesign.md) | Same equations, different constraints, and why no GSE library exists | **written** |
| [HazardousOperations.md](docs/HazardousOperations.md) | Clearing, the operation list, toxic against explosive, procedures | **written** |
| [ControlAndDataSystems.md](docs/ControlAndDataSystems.md) | Real-time against supervisory, interlocks, command paths, recording | **written** |
| [IntegrationAndProcessing.md](docs/IntegrationAndProcessing.md) | The flow, horizontal against vertical, transport, erection, mate | **written** |
| [StandardsIndex.md](docs/StandardsIndex.md) | One standard read in full and five not read | **written** |
| [ValidationReferences.md](docs/ValidationReferences.md) | The anchor, what it corrected, three gaps | **written** |

## Library

| Class | Computes | Status |
|---|---|---|
| `HazardSiting` | Explosive equivalent, separation rings, facility check, the hydrogen crossover | **written** |
| `PropellantLoading` | Tanking sequence, ground demand, hold sensitivity, scrub cost | **written** |
| `CountdownTimeline` | Critical path and float, recycle from a hold, turnaround, attempts | **written** |
| `LaunchAvailability` | Per-attempt and campaign probability, correlation, the lever comparison | **written** |

**Six things were deliberately not built**, and each has a stated reason in the worked example.

**GSE fluid analysis.** A ground half system is lines, valves, orifices, regulators and reliefs, and [fluidSystems](../fluidSystems/) computes all of it. A second implementation sized for heavier walls and lower cost would be the same equations with different inputs, and two of them drift. See [GSEDesign](docs/GSEDesign.md).

**Chill-down mass**, which [ChillDown](../propulsion/ignitionAndStart/) computes as an enthalpy balance including the factor of nine spread between its bounds for hydrogen. **Boil-off**, which [Insulation](../fluidSystems/) computes from the heat leak. Both are consumed here rather than reproduced.

**Umbilical retract dynamics**, a spring and a mass, which is [mechanismsAndSeparation](../mechanismsAndSeparation/). **Acoustic suppression**, whose environment belongs to [environmentsAndLoads](../environmentsAndLoads/). **Debris footprint**, which is [rangeSafetyAndFTS](../rangeSafetyAndFTS/).

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../common/](../common/) through this domain's `groundUtils.py`.

---

## Worked example

`codeInterface.py` takes a two stage vehicle through siting, tanking, countdown and campaign.

| Question | Answer |
|---|---|
| Hydrogen effective fraction, 38 t stage | 18.3 % against a flat 14 % |
| Where the hydrogen rule changes over | 84,635 kg |
| Inhabited building distance | 609 m |
| Tanking time, and what dominates it | 102 min, 64 % chill-down |
| Ground demand per attempt | 1.51 flight loads |
| Propellant lost on a scrub | 0.96 flight loads |
| Countdown against its serial sum | 220 min against 380 |
| Recycle from a 10 minute hold | 26 min |
| Turnaround, and what sets it | 48 h, hydrogen resupply |
| Go probability per attempt, six criteria | 60.5 % |
| Attempts: schedule against storage | 8 against **7** |

```bash
python groundSystemsAndOperations/codeInterface.py
```

---

## The anchor, and what it corrected

**DESR 6055.09 and NASA-STD-8719.12A were read in full** for the energetic liquid equivalence table, its hydrogen footnote, and the K factor table. Both are duplicated into [validation/referenceCases.py](../validation/referenceCases.py) and asserted against the library by a test.

Reading them corrected two things.

**The sixty per cent TNT equivalence commonly quoted for LO2/LH2 is not the siting rule.** It is a yield figure from the Project PYRO test series. The rule is the larger of `8 W**(2/3)` and fourteen per cent, and building on sixty per cent would have overstated a small stage by about a factor of three while missing the shape of the rule entirely.

**The standard's own bracketed metric coefficient does not convert.** It prints `8 W**(2/3)` in pounds and `4.13 Q**(2/3)` in kilograms; the exact conversion is 6.147, a factor of 1.488 larger. An SI-native reading gives a shorter siting distance than the form the table is built on. The library computes in the English form and a test asserts the discrepancy rather than correcting it silently.

**This is the second time in this repository that reading a standard rather than a summary changed a result.** The first was NASA-STD-5017B in [mechanismsAndSeparation](../mechanismsAndSeparation/). The pattern is consistent enough to be a rule.

Against that, AFSPCMAN 91-710 was not read, and it is the document that would turn most of the hazardous operations material from practice into requirement. See [ValidationReferences](docs/ValidationReferences.md).

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [fluidSystems](../fluidSystems/) | GSE is a fluid system; the analytical tools apply directly and are not duplicated here |
| [fluidSystemsTesting](../fluidSystems/fluidSystemsTesting/) | Test stands and launch pads share most of their design problems, and the standard has a column for each |
| [propulsion](../propulsion/) | Supplies the chill-down mass this domain totals over an attempt |
| [environmentsAndLoads](../environmentsAndLoads/) | Owns the acoustic environment the deluge is sized against, and the transport load case |
| [mechanismsAndSeparation](../mechanismsAndSeparation/) | Umbilical retract, hold-down release, and the ordnance this domain sequences around |
| [rangeSafetyAndFTS](../rangeSafetyAndFTS/) | Debris footprint and the flight termination requirements in AFSPCMAN 91-710 |
| [recoveryAndReusability](../recoveryAndReusability/) | Recovery and refurbishment run on the same ground infrastructure |

---

Sean Bowman
