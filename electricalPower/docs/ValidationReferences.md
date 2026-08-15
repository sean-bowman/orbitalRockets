[Home](../README.md) > Validation References

# Validation References

The external sources this domain's tools are checked against, and the several things they cannot check.

Kept separate from the reference lists at the foot of each document. Those are further reading; this is the material a test asserts against. The methodology is in [validation/README.md](../../validation/README.md).

| Level | Means |
|---|---|
| **Hardware** | Compared against measured or specified performance of real hardware |
| **Standard** | Reproduces a published standard or definition exactly. Catches an implementation error only |
| **Bounded** | No direct comparison, but the result is bracketed by something |
| **Unvalidated** | No external anchor. Recorded with what depends on it |

**This domain has the tightest single anchor in the repository and the longest list of unread standards.** Both are worth stating at the top, and the useful part is that they do not overlap: the exact anchor supports the domain's central result, and the unread standards support things the domain reports rather than concludes.

---

## The AWG definition

- **Source:** The American Wire Gauge definition, and the standard annealed copper resistivity of 1.724e-8 ohm m at 20 C
- **Validation level:** Standard, and exact
- **Relevance:** Every conductor resistance, and therefore every voltage drop, in the domain.
- **Key findings:**
  - `d(n) = 0.127 mm * 92 ** ((36 - n) / 39)`, with 36 AWG exactly 0.005 inches
  - Computed resistances reproduce published tables to **four significant figures** across 10 to 24 AWG, a worst-case relative error of 0.026 per cent
  - Three gauge steps double the conductor area, six quadruple it, ten are a factor of ten in resistance

**Why this one matters more than its size suggests.** The domain's central result is that voltage drop rather than ampacity chooses the wire gauge on a launch vehicle. Voltage drop is a pure resistance calculation and it is exact here. The ampacity side is representative, and it would have to be wrong by several gauge steps to change which constraint binds.

**So the conclusion rests on the validated half of the comparison**, which is an unusually comfortable position and is not the case anywhere else in this repository.

---

## The Panasonic NCR18650BF cell

- **Source:** Panasonic NCR18650BF cell specifications, from the manufacturer datasheet
- **Accessed:** 14 August 2026
- **Validation level:** Hardware. A manufacturer specification for a part that can be bought
- **Relevance:** The battery tables here are representative of a chemistry rather than of a part number, which is the right shape for a sizing library and is also a claim that nothing checked. **One real cell cannot validate a class figure. It can say whether the class figure errs the right way**, which is the only question a representative number has to answer.
- **Key findings:**
  - 3.200 A h rated at 20 C, 3.6 V nominal, 46.5 g bare, **248 W h/kg and 677 W h/l**
  - The library carries 200 W h/kg for lithium ion, **19 per cent below this cell.** A class figure has to cover older and higher rate chemistries as well, so below is the direction it should sit
  - The library's low temperature limit of -20 C for lithium ion **is exactly the cell's discharge floor**, which is the one place the two state the same quantity and it agrees

**Both published energy densities reproduce exactly from the rated capacity and the bare cell dimensions, and neither reproduces from the typical capacity.** Rated times nominal is 11.52 W h, which over 46.5 g is 247.7 W h/kg and over the 17.01 mL bare cell is 677.2 W h/l. **So a datasheet energy density is built from the rated figure at 20 C and not the typical figure at 25 C**, and the two differ by five per cent: multiplying a nameplate density by a typical capacity counts that five per cent twice. Both are asserted rather than noted.

**And the datasheet exposed a limit the library does not carry at all.** The cell discharges to -20 C and **cannot be charged below +10 C.** That is a hard limit rather than a derating curve, so no capacity factor expresses it, and the two ranges are thirty degrees apart. The consequence is operational rather than a sizing one: **a vehicle cold soaked on the pad can run its battery and cannot top it up.** A chemistry-level table cannot say that, which is the argument for having a real part alongside one.

**What the datasheet does not supply** is the capacity against temperature curve, which is published as a chart rather than a table. `TEMPERATURE_CAPACITY_FACTOR` is therefore still representative.

---

## Closed forms

- **Validation level:** Standard, and exact
- **Key findings:**
  - Voltage drop counts both conductors, and the factor of two is asserted rather than assumed
  - Copper resistance rises with the temperature coefficient, checked at an 80 K rise
  - Conductor area scales with the square of diameter
  - The energy rollup by phase equals the rollup by load, to machine precision
  - Source energy exceeds delivered energy by exactly the distribution efficiency
  - Battery derating is the product of its two factors
  - Solenoid hold power at half current is exactly a quarter of continuous

**The rollup cross-check earns its place.** Summing a power budget two ways, by phase and by load, is the arithmetic most likely to go wrong in a spreadsheet and the easiest thing to assert in a test.

---

## What is not validated

Three entries in [validation/referenceCases.py](../../validation/referenceCases.py) under `UNVALIDATED`, and each one names what survives it.

**Wire ampacity and derating** (`wireAmpacity`). AS50881 gives these as curves and the standard is not openly available. The ampacity-limited gauge moves with them. **The conclusion does not**: voltage drop rather than ampacity chooses the gauge, and that rests on the exact resistance calculation above. The derating would have to be wrong by several gauge steps to overturn it.

**Battery derating** (`batteryDerating`), partly closed. Depth of discharge, temperature capacity and pack fraction are still representative across a class. The chemistry specific energies are now bracketed by a real cell, above: the library sits 19 per cent below a current part, which is the direction a class figure should err in. Pack mass scales with all of them. **The structural result does not**: that the nameplate is close to twice the energy delivered once the two derations multiply, and that neither is a margin, holds for any plausible values.

**What is left is the temperature curve**, which the datasheet publishes as a chart rather than a table. That is a harder gap than it looks, because reading numbers off a chart and recording them as a specification is exactly the kind of provenance this directory exists to prevent.

**Harness routing and connector mass** (`harnessRoutingAllowance`). Representative. Harness mass scales with them, and harness mass is reliably underestimated. **The argument is about the method rather than the numbers**: a counted estimate with imperfect factors converges as the design matures and a fractional one does not. This is also the one gap in the repository that could be closed with a set of scales.

---

## What is not modelled at all

Distinct from unvalidated, and listed because a reader should not have to infer it.

**Grounding topology and EMI magnitudes.** No scalar answer exists for the first and the second is measured against MIL-STD-461, which was not read. Both are documented in [GroundingAndBonding](GroundingAndBonding.md) and [EMIAndEMC](EMIAndEMC.md).

**Fault current and protection coordination.** Needs a source impedance model, principally the battery's internal resistance and its variation with state of charge and temperature.

**Bus transient response.** The same gap. [PowerQuality](PowerQuality.md) describes the disturbances and computes only the steady-state drop.

**Battery thermal runaway.** A safety analysis rather than an energy one.

**The firing circuit.** Deliberately not built here; it lives in [mechanismsAndSeparation](../../mechanismsAndSeparation/docs/Pyrotechnics.md). See [PyroCircuits](PyroCircuits.md).

**A cell datasheet closes three of those five**, which makes it worth more than any of the standards on the unread list.

---

## The shape of what is here

The domain divides cleanly and it is worth naming the line.

**What it concludes** rests on exact arithmetic: the gauge is chosen by voltage drop, copper falls with the square of bus voltage, hold power is a quarter of continuous, the nameplate is twice the delivered energy. Every one of those is a ratio or an identity, and every one survives its representative inputs being wrong.

**What it reports** rests on unread standards: an ampacity in amps, an emissions limit, a power quality tolerance. Those are stated as representative and they are the numbers a real programme would replace first.

**And what it documents** rests on nothing computable at all: grounding topology, EMC practice, test order. Those are written down because they are decisions rather than calculations, and because the domain that touches every other subsystem is mostly made of decisions.
