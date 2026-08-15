[Home](../README.md) > Validation References

# Validation References

The external material this domain's tools are checked against, and what they cannot check.

Kept separate from the reference lists at the foot of each document. Those are further reading; this is the material a test asserts against. The methodology is in [validation/README.md](../../validation/README.md).

| Level | Means |
|---|---|
| **Hardware** | Compared against measured or specified performance of real hardware |
| **Standard** | Reproduces a published standard or definition exactly. Catches an implementation error only |
| **Bounded** | No direct comparison, but the result is bracketed by something |
| **Unvalidated** | No external anchor. Recorded with what depends on it |

**This domain is anchored to two closed forms rather than to a standard**, which is unusual here and is stronger than it sounds: a derivation either follows or it does not. Against that, everything operational and economic is representative.

---

## The Allen-Eggers solution

- **Source:** H. J. Allen and A. J. Eggers, NACA Report 1381, 1958. Relations read from the NASA TFAWS 2012 aerothermodynamics course notes
- **Validation level:** Standard, and exact
- **Relevance:** Every entry quantity the domain computes
- **Key findings:**
  - `a_max = V_e^2 sin|gamma| / (2 e H)`, independent of the ballistic coefficient
  - Peak deceleration at `V = V_e exp(-1/2) = 0.6065 V_e` and `rho = beta sin|gamma| / H`
  - Peak heating at `V = V_e exp(-1/6) = 0.8465 V_e` and `rho = beta sin|gamma| / (3 H)`
  - `q_max ~ sqrt(beta sin|gamma| / Rn) V_e^3`
  - `Q ~ V_e^2 sqrt(pi beta H / (Rn sin|gamma|))`, from the closed integral

**Every one of those is asserted by a test**, and the invariance of peak deceleration is asserted across a factor of a thousand in ballistic coefficient rather than a plausible range.

---

## A correction to the source

The course notes state that peak heating sits at about 1.1 times the altitude of peak deceleration.

**That ratio holds only for an orbital entry.** The two peak densities differ by exactly a factor of three, and altitude is logarithmic in density, so what is fixed is the **separation**:

```
h_q - h_g = H ln(3) = 7.9 km, for every entry of every vehicle
```

For an orbital entry the deceleration peak is high enough that 7.9 km is about a tenth of it, which is where 1.1 comes from. **On a booster returning from a lofted suborbital trajectory the peaks sit near 16 and 24 km and the ratio is 1.5.**

**This library reports the separation**, and a test asserts it equals `H ln(3)` exactly. It is a generalisation of the source rather than a disagreement with it.

---

## The Sutton-Graves constant

- **Source:** K. Sutton and R. A. Graves, NASA TR R-376, 1971. Constant read from the NASA TFAWS 2012 course notes
- **Validation level:** Bounded
- **Relevance:** Every heat flux and heat load in the domain

**The units on this constant are quoted inconsistently and it matters by four orders of magnitude.** Several sources state that

```
q = 1.7415e-4 sqrt(rho / Rn) V^3
```

returns W/cm2 with density in kg/m3, nose radius in metres and velocity in m/s. **It does not; it returns W/m2.**

Fixed here by reproducing published entry cases rather than by trusting the statement:

| Case | Conditions | Computed | Published |
|---|---|---|---|
| Stardust | 12.6 km/s, Rn 0.23 m | 1,027 W/cm2 | ~1,200 peak convective |
| Apollo | 11.1 km/s, Rn 4.69 m | 196 W/cm2 | ~200 to 250 convective |

**Both land where they should read as W/m2 and are absurd by 1e4 read as W/cm2.** A test asserts the two cases rather than the units statement.

**This is BOUNDED rather than validated**, and the distinction is deliberate. The two cases bracket the correlation to within tens of per cent, and the densities used are read off a standard atmosphere at the published peak heating altitudes rather than taken from the flight reconstructions. **It is enough to fix the units convention, which is what it was done for, and not enough to claim the correlation itself is reproduced.**

---

## The published payload penalty

- **Source:** `LAUNCH_VEHICLES['Falcon 9 Block 5']` in [validation/referenceCases.py](../../validation/referenceCases.py)
- **Validation level:** Hardware, for the ratio
- **Key findings:**
  - Low orbit: 22,800 kg expended against 18,500 reusable, a penalty of 18.9 per cent
  - Transfer orbit: 8,300 against 5,500, a penalty of 33.7 per cent
  - Both from one source table, so the ratio is sourced even though the model behind it is not

**The bottom-up budget over-predicts by 25 per cent at low orbit and by more at transfer orbit.**

**That is reported rather than tuned away, and the direction of the error is informative**: a single pair of exchange ratios belongs to one stack flown to one staging velocity, and the transfer orbit mission is not that one.

**Tuning the ratios until the budget reproduced the published penalty and then reporting the agreement would be calibration, not validation.** The class inverts instead, and with both exchange ratios now computed by [vehicleArchitecture](../../vehicleArchitecture/) the inversion has one unknown rather than two. It says the stage holds back 6.2 per cent of its propellant load against the 9 assumed, and that reserve buys 1,937 m/s on the landed mass, which is an entry burn and a landing burn without boost-back. **The delta-V check is the part that matters**: an inverted number that could not be turned back into a descent profile would be an artefact.

---

## The precedent figures

- **Validation level:** Bounded
- **Key findings:**
  - Space Shuttle orbiter design turnaround 14 days, about 160 hours of work
  - Shortest achieved turnaround 54 days, Atlantis between STS-51-J and STS-61-B in 1985
  - Discovery flew 39 missions
  - Falcon 9 booster B1088 turned around in 9 days 3 hours
  - Falcon 9 booster B1067 reached 36 flights by July 2026, against a stated qualification goal of 40

**These bound the domain's central claim** rather than validating a calculation: that reuse is an inspection problem before it is a landing problem, and that a design which makes inspection expensive cannot be turned around quickly however well it lands.

---

## Closed forms

- **Validation level:** Standard, and exact
- **Key findings:**
  - Touchdown load factor is exactly inverse in stroke, and `requiredStroke` inverts `calculateLoadFactor` to machine precision
  - The exponential atmosphere inverts exactly
  - Peak flux scales as the square root of beta and the cube of entry velocity, asserted numerically
  - Heat load scales as the square root of beta and inversely with the square root of steepness
  - The payload penalty shares sum to one
  - The break-even matches `1 / (1 - refurbishment - recovery)`
  - Expected flights equal planned flights at perfect recovery

---

## What is not validated

Three entries in [validation/referenceCases.py](../../validation/referenceCases.py) under `UNVALIDATED`, each naming what survives it.

**Exchange ratios** (`exchangeRatios`), largely closed and worth reading for what closing it found. Both ratios are now computed by `StagedVehicle.exchangeRatios` from the published Falcon 9 stage masses rather than assumed, and the ratio between them is not an estimate at all: it is `1 - 1/R` exactly, asserted against the measured value on four vehicles. **What remains is that the absolute values need the two specific impulses, which the register states are not published in the same source as the masses.** Swinging both by five per cent moves each ratio by under three per cent and the ratio between them not at all.

**Wiring the two domains together reversed the ordering this domain had assumed.** The reserve costs more per kilogram than the dry mass, not less, and the class guard that enforced the old ordering would have refused the correct pair. The reason written down beside the old assumption was that a reserve is carried for less of the burn than a landing leg, which does not survive being examined: a recovery reserve is spent after separation and is aboard for the whole ascent. **A plausible reason next to a wrong number is harder to catch than a bare number**, and this one sat there through a full domain build.

**Life damage rates** (`lifeDamageRates`). Representative of the items that usually set a refurbishment interval rather than measured for any article. Every flight count scales with them. **The structural results do not**: that one item limits and extending it buys the gap to the next is the same arithmetic as a turnaround driver, and that the limiting item is not the one that looks worst is a statement about appearance and damage rate being unrelated.

**Recovery mode fractions and absorber efficiencies** (`recoveryModeFractions`). Representative. The penalty by mode and the load factor scale with them. **The orderings do not**: a return to the launch site costs more because it cancels and reverses the downrange velocity, and a crushable core fills its force-stroke rectangle better than a damper because a damper force follows a velocity going to zero. Both are mechanisms.

---

## What is not modelled at all

**Lift.** The entry solution is ballistic. A lifting entry flies a different corridor with a different solution.

**Radiative heating.** Negligible at booster speeds and a large fraction at lunar return speeds.

**Anything but the stagnation point.** The flux distribution over the body is a computational fluid dynamics problem.

**Fatigue and crack growth.** [aerospaceMaterials](../../aerospaceMaterials/) owns Paris law and the material data. This domain counts flights against a damage per flight and does not derive that damage from a stress.

**Parachutes.** A drag area and a deployment transient.

**Guidance to the landing point**, and the sea state that produces a deck slope.

**Refurbishment cost breakdown.** Taken as a fraction and shown to be the term that decides everything.

---

## The shape of what is here

**What the domain concludes about entry** rests on a 1958 derivation, and it is exact: peak deceleration does not depend on the vehicle, the corridor trades peak rate against total load in opposite directions, and the two peaks are separated by `H ln 3`.

**What it concludes about reuse** rests on arithmetic that survives its inputs: products, sums, geometric expectations and one-limiting-item orderings.

**What it reports** rests on representative tables that a real programme would replace from its own records, and on one published payload penalty that the model over-predicts and says so.

**And what it documents** rests on almost no standard at all, because reusable launch does not have one. That is stated in [StandardsIndex](StandardsIndex.md) rather than implied.
