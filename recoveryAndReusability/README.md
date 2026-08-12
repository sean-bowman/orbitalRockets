# recoveryAndReusability

**Recovery, Entry, Landing and Refurbishment**

> **Status: complete.** Five classes, twelve documents and 80 tests, anchored to two closed forms, one of which was generalised and one of whose published units were wrong by four orders of magnitude.

---

## What This Is

Reuse changes the economics of launch and it changes the engineering everywhere. This domain covers the flight side (entry, descent, landing) and the ground side (inspection, refurbishment, life tracking) along with the economics that decide whether reuse is worth the performance it costs.

**The interesting engineering is not the landing.** It is designing hardware whose condition after flight can be established cheaply enough to fly it again.

---

## The five results

**Peak deceleration does not depend on the vehicle.** Allen and Eggers solved ballistic entry in closed form in 1958, and the maximum g is `V_e^2 sin|gamma| / (2 e H)`: entry velocity, flight path angle and atmospheric scale height, and nothing about the body. Across a factor of sixteen in ballistic coefficient the peak g does not move at all. What moves is the heating, by four times, because peak flux goes as the square root of the ballistic coefficient. **A heavy entry is a hot entry, not a high-g one.**

**A booster entry is a different problem from an orbital one by a factor of twenty two in heat flux**: 18 W/cm2 against 390. Peak flux goes as the cube of entry velocity and a first stage returns from a lofted suborbital arc at a quarter of orbital speed. **Eighteen watts per square centimetre is a paint problem and four hundred is a heat shield**, which is the whole reason first stage reuse arrived long before upper stage reuse.

**Reserve propellant costs nearly five times the payload that recovery hardware does**, even though the hardware is what gets designed, weighed and argued about. And the penalty in kilograms is fixed while the payload it eats into is not, so the penalty as a fraction rises with mission difficulty: **that is why boosters are expended on the hardest missions of an otherwise reusable fleet.**

**Stroke is the cheap variable at touchdown.** Load factor is inversely proportional to it, so a reusable damper, which fills barely half its force-stroke rectangle against a crushable core's four fifths, is bought back with 1.5 times the travel rather than with structure. **The reusable absorbers are the inefficient ones and that is not a coincidence**: a damper force follows a velocity that is going to zero by definition.

**Two thirds of the benefit of reuse arrives by the third flight.** The amortised unit cost collapses and the recurring terms do not, so once the flight count is high **the refurbishment cost is the whole game**. And a three per cent recovery loss rate removes 24 per cent of the planned flights, because the losses compound over the fleet life.

---

## Design Ethos

- Reuse is an inspection problem before it is a landing problem.
- Every kilogram of recovery hardware is paid on every flight, including the ones that do not recover.
- Design for inspectability or accept teardown. There is no third option.
- Life tracking only works if the flight environment was actually measured.
- The break-even flight count is the real figure of merit, not the fact of reuse.
- Once the flight count is high, argue about refurbishment cost. Nothing else moves.

---

## Documentation

| Document | Covers | Status |
|---|---|---|
| [RecoveryOverview.md](docs/RecoveryOverview.md) | Hub: what the domain found, the five questions, document index | **written** |
| [EntryAerodynamics.md](docs/EntryAerodynamics.md) | Allen-Eggers, the peaks, the corridor trade, why a booster is not a capsule | **written** |
| [DescentAndLanding.md](docs/DescentAndLanding.md) | Propulsive against parachute, touchdown energy, absorbers, tipover | **written** |
| [RecoveryHardware.md](docs/RecoveryHardware.md) | Hardware and reserve, what each costs, using a published penalty honestly | **written** |
| [RecoveryOperations.md](docs/RecoveryOperations.md) | Safing, ships, transport, and the operation nobody budgets | **written** |
| [InspectionAndAcceptance.md](docs/InspectionAndAcceptance.md) | The ladder, proof as an inspection, disposition, designing for access | **written** |
| [RefurbishmentProcess.md](docs/RefurbishmentProcess.md) | The flow, where the cost goes, replacement policy, the Shuttle precedent | **written** |
| [LifeTrackingAndLimits.md](docs/LifeTrackingAndLimits.md) | Miner's rule, the limiting item, fleet leader, demonstrated against certified | **written** |
| [FluidSystemReuse.md](docs/FluidSystemReuse.md) | Seals, valves, contamination, and whether it can be cleaned in place | **written** |
| [ReuseEconomics.md](docs/ReuseEconomics.md) | Break-even, the flight count curve, recovery losses, cost per kilogram | **written** |
| [StandardsIndex.md](docs/StandardsIndex.md) | Two closed forms, and less governing standard than any other domain here | **written** |
| [ValidationReferences.md](docs/ValidationReferences.md) | The anchors, one generalisation, one units correction, three gaps | **written** |

## Library

| Class | Computes | Status |
|---|---|---|
| `EntryTrajectory` | Allen-Eggers peaks, heat flux and load, the beta and corridor sweeps | **written** |
| `RecoveryBudget` | Hardware mass, reserve, payload penalty by mode, the published-penalty inversion | **written** |
| `LandingLoads` | Touchdown load factor, required stroke, absorber comparison, tipover | **written** |
| `LifeTracking` | Damage accumulation, the limiting item, fleet leader, certification gap | **written** |
| `ReuseEconomics` | Cost per flight, break-even, recovery losses, cost per kilogram | **written** |

**`EntryTrajectory` was added beyond the plan.** The scaffold listed four classes and none of them computed an entry, which left the domain taking a heat flux from [thermalManagement](../thermalManagement/) that nothing produced. It is the domain's strongest result and its only exact one.

**Six things were deliberately not built.** Aeroheating into a structure ([thermalManagement](../thermalManagement/) and [environmentsAndLoads](../environmentsAndLoads/)); fatigue and crack growth ([aerospaceMaterials](../aerospaceMaterials/), which owns Paris law); the payload exchange ratios ([vehicleArchitecture](../vehicleArchitecture/), whose mass chain defines them); parachute sizing; guidance to the landing point, which [avionicsAndGNC](../avionicsAndGNC/) declined for reasons that apply here too; and the sea state behind a droneship deck slope.

All classes follow the repository interface: `setInputs()`, `calculate*()` or `size*()`, `generateReport()`. Shared helpers come from [../common/](../common/) through this domain's `recoveryUtils.py`.

---

## Worked example

`codeInterface.py` takes one booster through entry, recovery cost, touchdown, life and economics.

| Question | Answer |
|---|---|
| Peak deceleration, over 16x in beta | 5.3 g, **unchanged** |
| Peak heat flux over the same range | 4.0x |
| Booster against orbital entry, flux | 18 against 390 W/cm2 |
| Peak altitude separation | 7.9 km, always |
| Reserve against hardware, in payload | 4.8x |
| Recovery penalty, low orbit | 23.5 % modelled, 18.9 % published |
| Touchdown load factor | 1.82 g on 450 mm |
| What limits the article | engine turbopump, 5 flights left |
| Benefit of reuse by the third flight | 68 % |
| Planned against expected flights | 20 against 15.2 |
| Cost per flight against per kilogram | 65 % against 57 % |

```bash
python recoveryAndReusability/codeInterface.py
```

---

## The anchors, and what they corrected

**Allen and Eggers, NACA Report 1381 (1958)** is a derivation rather than a standard, which makes it stronger: it either follows or it does not. Every relation is asserted by a test, including the invariance of peak deceleration across a factor of a thousand in ballistic coefficient.

**One generalisation of the source.** The course notes teaching those relations state that peak heating sits at about 1.1 times the altitude of peak deceleration. That ratio holds only for an orbital entry. The two peak densities differ by exactly a factor of three, so what is fixed is the **separation**, `H ln 3` or 7.9 km, for every entry of every vehicle. On a booster returning from a suborbital arc the ratio is 1.5.

**Sutton and Graves, NASA TR R-376 (1971)** supplies the heating correlation, and **its published units are wrong by four orders of magnitude in several sources.** They state the expression returns W/cm2 with SI inputs; it returns W/m2. Fixed by reproducing published entry cases rather than by trusting the statement: Stardust computes to 1,027 W/cm2 against ~1,200 published, Apollo to 196 against ~200 to 250. Both are absurd by 1e4 read the other way.

**And the Falcon 9 payload penalty is used by inversion rather than by calibration.** The bottom-up budget over-predicts by 25 per cent; tuning the exchange ratios until it matched and then reporting the agreement would be calibration. The class inverts instead and reports what the vehicle implies: 0.240 kg of payload per kilogram of dry mass against 0.300 assumed, an honest 80 per cent.

**Reusable launch has less governing standard behind it than any other subject in this repository**, which is a fact about the subject. See [StandardsIndex](docs/StandardsIndex.md).

---

## Where this domain connects

| Domain | Interaction |
|---|---|
| [vehicleArchitecture](../vehicleArchitecture/) | Owns the payload exchange ratios and publishes the recovery penalty this domain builds from parts |
| [thermalManagement](../thermalManagement/) | Sizes the protection that survives the entry flux computed here, repeatedly |
| [environmentsAndLoads](../environmentsAndLoads/) | Owns the aeroheating environment and the transport load case |
| [aerospaceMaterials](../aerospaceMaterials/) | Owns Paris law and the damage tolerance that life tracking counts against |
| [fluidSystems](../fluidSystems/) | Seals, valves and cleanliness after a flight are the refurbishment driver |
| [groundSystemsAndOperations](../groundSystemsAndOperations/) | Recovery runs on the same infrastructure, and safing follows the same conventions |
| [reliabilityAndMissionAssurance](../reliabilityAndMissionAssurance/) | Life limits and usage monitoring are reliability instruments |

---

Sean Bowman
