[Home](../README.md) > Validation References

# Validation References

The external sources this domain's tools are checked against, and the several things they cannot check.

Kept separate from the reference lists at the foot of each document. Those are further reading; this is the material a test asserts against. The methodology is in [validation/README.md](../../validation/README.md).

| Level | Means |
|---|---|
| **Hardware** | Compared against measured or specified performance of real hardware |
| **Standard** | Reproduces a published formula exactly. Catches an implementation error only |
| **Bounded** | No direct comparison, but the result is bracketed by something |
| **Unvalidated** | No external anchor. Recorded with what depends on it |

**This domain validates its bookkeeping and not its models**, and the distinction is sharper here than anywhere else in the repository. The rocket equation is exact. What is uncertain is every mass estimate feeding it, and those are the numbers a published vehicle gives as answers rather than as inputs.

---

## Falcon 9 Block 5 stage masses

- **Source:** <https://en.wikipedia.org/wiki/Falcon_9_Block_5>, and the SpaceX specifications it cites
- **Accessed:** 09 August 2026
- **Validation level:** Hardware
- **Relevance:** The only external anchor this domain has. Published stage masses put through the rocket equation have to land near the delta-V a real mission needs.
- **Key findings:**
  - Stage 1: dry 22,200 kg, gross 433,100 kg, propellant 410,900 kg as 287,400 LOX and 123,500 RP-1
  - Stage 2: dry 4,000 kg, gross 111,500 kg, propellant 107,500 kg as 75,200 LOX and 32,300 RP-1
  - Payload to LEO at 28.5 degrees: **22,800 kg expended, 18,500 kg reusable**
  - Structural coefficients against gross mass: **0.0513 and 0.0359**
  - Through the rocket equation with a 22.8 t payload: 3751 and 5500 m/s, **9252 m/s total** at a 567 t liftoff mass
  - A low Earth orbit mission needs about 9300 m/s including losses, so this closes to within a few per cent

**A useful internal check on the source itself.** The mixture ratios implied by the tabulated propellant loads are 2.327 and 2.328 on the two stages. Four numbers read from a table agreeing to three figures on a derived quantity is good evidence they came from a consistent source.

**What this validates.** The bookkeeping: each stage lifts everything above it, and the burnout mass includes the stage's own dry mass. That is the thing that goes wrong quietly, producing a plausible number rather than an error.

**What it does not validate.** Any mass estimating relationship in this domain. These masses are answers, not inputs. A domain that predicted them from a payload requirement would be validated by them; this one takes them as given.

**The weakest link, stated.** Specific impulse is not published in the same source. The values used, about 297 s effective for the first stage and 348 s for the second, are widely cited rather than sourced alongside the masses, and they carry lower confidence than the masses do. **So the delta-V check is good to a few per cent rather than to one**, and a test asserts that caveat stays recorded.

---

## The recovery penalty

- **Source:** as above, both figures from the same table
- **Validation level:** Hardware, for the ratio
- **Key findings:**
  - LEO: 22,800 kg expended against 18,500 kg reusable, a **penalty of 18.9 per cent**
  - GTO: 8,300 kg expended against 5,500 kg reusable, a **penalty of 33.7 per cent**
- **Why the ratio is the sourced quantity:** neither number is something this repository can reproduce, because recovery propellant, entry burn and landing burn are all outside it. But both come from one table, so their ratio is sourced even though the model behind them is not.
- **What the difference between the two says:** the same recovery hardware and propellant is a larger share of a smaller performance margin. GTO leaves less to give.

See [ReusabilityImpacts](ReusabilityImpacts.md).

---

## Closed forms

- **Validation level:** Standard, and exact
- **Key findings:**
  - Tsiolkovsky reproduces its own definition, and gives zero at a mass ratio of one and `c` at a mass ratio of `e`
  - The Lagrange staging condition returns a split summing exactly to the target, asserted to one part in a million
  - Sizing and performance are inverses: size a vehicle to a delta-V, then compute what the sized vehicle delivers, and the two agree to one part in a million
  - The rotation assist is largest due east at the equator and zero due south

**That last set of round trips caught two real defects.** An inverted bisection and an overshooting bracket search both produced results that looked reasonable in isolation, and both were caught by asserting that the optimiser's split sums to what it was asked for.

---

## What is not validated

Three entries in [validation/referenceCases.py](../../validation/referenceCases.py) under `UNVALIDATED`.

**The ascent loss model** (`ascentLossModel`). Representative reference losses and power-law exponents rather than a trajectory integration. The absolute loss total, and therefore the delta-V target every vehicle here is sized to, moves with them. **The conclusion drawn does not**: that the loss-minimising thrust to weight sits far above the practical band holds for any exponent pair where gravity loss falls faster than drag loss rises, which is the whole plausible range.

**The non-tank dry fraction** (`nonTankDryFraction`). Engines, thrust structure, avionics, feed lines and skirts as a single fraction of propellant mass. It is doing as much work as the tank model in setting the structural coefficient, and unlike the tank model it is a constant rather than a calculation. **This is the most tractable gap in the whole register**: every part of it is owned by a domain this repository has already built, so it could be assembled rather than assumed.

**The mass growth allowance table** (`massGrowthAllowance`). The shape follows AIAA and ANSI mass properties practice; the specific percentages were not taken from the standard, which was not read. The distinction the domain actually makes, that growth allowance and margin are different things, is structural and does not depend on the values.

---

## The shape of what is here

The pattern is worth naming because it differs from the propulsion domains.

**The physics is exact and the inputs are guesses.** The rocket equation needs no validation. Every mass feeding it is an estimate, and the domain's honest position is that it computes exactly what follows from numbers it cannot check.

So the results this domain claims are all **relative**: the staging optimum is flat, the elasticity scales inversely with payload fraction, a tank kilogram costs eleven at liftoff, pressure feeding nearly doubles the vehicle. Every one of those is a ratio or a shape, and every one survives its inputs being wrong by a reasonable factor.

**The absolute numbers are illustrative and the relationships are the product.** That is stated here rather than left for a reader to infer from the register.
