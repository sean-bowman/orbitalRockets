[Home](../README.md) > Propellant Selection

# Propellant Selection

## Contents

- [Overview](#overview)
- [The two figures of merit disagree](#the-two-figures-of-merit-disagree)
- [Bulk density and the volume split](#bulk-density-and-the-volume-split)
- [Storability](#storability)
- [Mixture ratio and why peak impulse is fuel rich](#mixture-ratio-and-why-peak-impulse-is-fuel-rich)
- [What the table does not tell you](#what-the-table-does-not-tell-you)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Propellant selection looks like a single-objective problem and is not. There are at least three objectives that rank the candidates differently, and the stage decides which one is in charge.

The mistake this document exists to prevent is choosing on specific impulse alone. It is the number everyone quotes, it is genuinely the right objective for some stages, and it is the wrong one for a first stage.

---

## The two figures of merit disagree

**Specific impulse** is impulse per unit propellant mass. It decides how much propellant a mission needs.

**Density impulse**, `rho_bulk Isp`, is impulse per unit propellant volume. It decides how large the tanks holding it are, and those tanks are structure that has to be carried, insulated and pushed through the atmosphere.

All at an area ratio of 40, so the expansion is not doing the ranking:

| Combination | `Isp` [s] | `rho_bulk` [kg/m^3] | `rho.Isp` [10^3 kg s/m^3] | Storable |
|---|---|---|---|---|
| H2O2/RP-1 | 307.6 | 1309 | 402.8 | Yes |
| N2O4/MMH | 328.1 | 1199 | 393.4 | Yes |
| N2O4/UDMH | 324.4 | 1176 | 381.5 | Yes |
| LOX/RP-1 | 342.8 | 1024 | 350.8 | No |
| LOX/ethanol | 311.8 | 974 | 303.7 | No |
| LOX/LCH4 | 356.8 | 826 | 294.7 | No |
| LOX/LH2 | 447.7 | 344 | 153.9 | No |

**The two columns are in nearly opposite order.** LOX/LH2 leads specific impulse by 31 per cent over LOX/RP-1 and trails it on density impulse by a factor of 2.3. Against H2O2/RP-1 the density impulse factor is 2.6.

That is why almost no first stage has flown on hydrogen without solid boosters beside it, and why hydrogen upper stages are common. A first stage carries its tanks through the atmosphere and pays for their volume in structure, drag and gravity losses. An upper stage in vacuum is closer to a pure specific impulse problem.

**Fixing the area ratio is what makes the comparison mean anything.** A combination expanded further looks better on specific impulse, and that is a nozzle decision rather than a propellant one. The [PropellantCombination](#tool-interface) class fixes it for this reason.

---

## Bulk density and the volume split

```
rho_bulk = (1 + MR) / (MR / rho_ox + 1 / rho_fuel)
```

A harmonic mean weighted by mass fraction, which sits nearer the lower of the two densities than an arithmetic average suggests.

**The number that actually decides the vehicle layout is not the mixture ratio, it is the volume split.**

| Combination | `MR` | Fuel share of volume | Fuel share of mass |
|---|---|---|---|
| H2O2/RP-1 | 7.30 | 19.5 % | 12.0 % |
| LOX/RP-1 | 2.56 | 35.5 % | 28.1 % |
| N2O4/UDMH | 2.61 | 41.1 % | 27.7 % |
| N2O4/MMH | 2.16 | 43.2 % | 31.6 % |
| LOX/LCH4 | 3.45 | 43.9 % | 22.5 % |
| LOX/ethanol | 1.60 | 47.5 % | 38.5 % |
| **LOX/LH2** | **5.50** | **74.5 %** | **15.4 %** |

**LOX/LH2 puts three quarters of its propellant volume in the fuel tank while that fuel is 15 per cent of the mass.** A layout drawn from the mixture ratio has the tanks the wrong way round, and the error is not subtle: it is a factor of five in tank volume.

The fuel volume fraction exceeds the fuel mass fraction for every combination in the table, because the fuel is the less dense of the two in all of them. The gap is the interesting part, and it is largest exactly where the specific impulse is best.

---

## Storability

A third axis, orthogonal to both figures of merit, and it decides what missions a stage can fly rather than how well it flies them.

**Storable** means the propellant stays liquid at ambient temperature without active management. It buys long coast, restart after a coast, and a vehicle that can sit loaded. N2O4 with MMH or UDMH is the classic pairing and it is hypergolic as well, which removes the igniter and its failure modes.

The cost is toxicity. N2O4 and the hydrazines are acutely toxic and carcinogenic, they need self-contained breathing apparatus and a scrubber, and the ground handling cost is real and permanent.

**Cryogenic** means active management, boiloff, chilldown, and a vehicle that cannot sit loaded indefinitely. In exchange, LOX is cheap, abundant and not toxic.

**H2O2 with RP-1 is the interesting corner.** Storable, non-toxic, the best density impulse in the table, and it pays 35 seconds of specific impulse against LOX/RP-1 for it. High-test peroxide also decomposes slowly in storage and is sensitive to contamination, which is a materials compatibility problem rather than a performance one. See [MaterialsCompatibility](../../fluidSystems/fluidSystemsLibrary/docs/MaterialsCompatibility.md).

---

## Mixture ratio and why peak impulse is fuel rich

Every operating mixture ratio in the table is below its stoichiometric value:

| Combination | Operating `MR` | Stoichiometric `MR` | Ratio |
|---|---|---|---|
| LOX/RP-1 | 2.56 | 3.41 | 0.75 |
| LOX/LH2 | 5.50 | 7.94 | 0.69 |
| LOX/LCH4 | 3.45 | 3.99 | 0.86 |
| N2O4/MMH | 2.16 | 2.50 | 0.86 |
| H2O2/RP-1 | 7.30 | 8.01 | 0.91 |

The reason is in `c* = sqrt(R Tc) / Gamma`, with `R` inversely proportional to molar mass, so `c*` goes as `sqrt(Tc / M)`.

Stoichiometric burning maximises `Tc`. Adding fuel past that point lowers `Tc`, **and lowers `M` faster**, because the excess fuel and its dissociation products are lighter than the combustion products. The ratio `Tc/M` therefore peaks fuel rich of stoichiometric.

**LOX/LH2 is the extreme case at 69 per cent of stoichiometric**, because hydrogen is the lightest thing available and the molar mass effect is enormous. It is also why the tabulated molar mass of 13 g/mol at `MR` 5.5 is not the 10 g/mol quoted at `MR` 4.0: the exhaust gets heavier as the mixture leans out, and a molar mass quoted without its mixture ratio is not usable.

Running fuel rich has a second benefit that has nothing to do with impulse: **it keeps the chamber wall away from an oxidising environment.** An oxidiser rich chamber attacks its wall rather than cooling it, which is why oxidiser rich operation appears in staged combustion preburners with deliberate material selection and essentially nowhere else.

---

## What the table does not tell you

The tabulated performance is a single point on a surface, and the class reports the reference condition alongside every number for that reason.

**`c*` moves with chamber pressure**, rising slowly as higher pressure suppresses dissociation. The table is taken at 6.9 MPa and using it at 20 MPa is conservative rather than wrong.

**`c*` moves with mixture ratio**, and the chamber temperature and molar mass that produce it move with it. Supplying a different mixture ratio to the class is allowed and flagged, because the other tabulated properties do not travel with it.

**CEA is the authority.** Anything past a trade study should replace these with a run at the actual chamber pressure and mixture ratio. The table exists so a first pass runs without a CEA installation, not so that CEA can be skipped.

---

## Design rules of thumb

- **Choose on density impulse for a first stage** and closer to specific impulse for an upper stage.
- **Fix the area ratio before comparing.** Otherwise the expansion does the ranking.
- **Lay the vehicle out from the volume split, not the mixture ratio.**
- **Treat storability as a mission requirement, not a performance axis.** It decides what the stage can do rather than how well.
- **Run fuel rich of stoichiometric**, for impulse and for the chamber wall.
- **Quote molar mass with its mixture ratio** or it is not usable.
- **Replace the table with CEA** before anything downstream of a trade study.

---

## Failure modes

**Selecting on specific impulse for a booster.** The classic error, and it points at hydrogen, which is the worst density impulse available.

**Comparing combinations at different area ratios.** The expansion does the ranking and the conclusion is about nozzles.

**Laying out tanks from the mixture ratio.** A factor of five error on LOX/LH2.

**Using a molar mass at the wrong mixture ratio.** 10 g/mol and 13 g/mol are both correct for LOX/LH2 at different operating points, and the difference is 12 per cent in `c*`.

**Running oxidiser rich without intending to.** The chamber wall is the thing that finds out.

**Treating the tabulated `c*` as pressure independent.** It is conservative at high chamber pressure, which is the safe direction, and it is still wrong.

---

## Worked numbers

All at an area ratio of 40, produced by running the code.

| Combination | `Isp` [s] | `rho_bulk` [kg/m^3] | `rho.Isp` [10^3] | Fuel volume share |
|---|---|---|---|---|
| H2O2/RP-1 | 307.6 | 1309.3 | 402.8 | 19.5 % |
| N2O4/MMH | 328.1 | 1198.9 | 393.4 | 43.2 % |
| N2O4/UDMH | 324.4 | 1176.0 | 381.5 | 41.1 % |
| LOX/RP-1 | 342.8 | 1023.5 | 350.8 | 35.5 % |
| LOX/ethanol | 311.8 | 973.9 | 303.7 | 47.5 % |
| LOX/LCH4 | 356.8 | 826.0 | 294.7 | 43.9 % |
| LOX/LH2 | 447.7 | 343.8 | 153.9 | 74.5 % |

Key ratios:

| Comparison | Value |
|---|---|
| LOX/LH2 specific impulse over LOX/RP-1 | +31 % |
| LOX/RP-1 density impulse over LOX/LH2 | 2.28x |
| H2O2/RP-1 density impulse over LOX/LH2 | 2.62x |
| LOX/LH2 fuel volume share against mass share | 74.5 % against 15.4 % |

---

## Standards

| Standard | What it gives you |
|---|---|
| NASA RP-1311 | CEA theory and usage, the source of equilibrium performance |
| MIL-PRF-25576 | RP-1 specification |
| MIL-PRF-27401 | Nitrogen tetroxide specification |
| MIL-PRF-27404 | MMH specification |
| MIL-PRF-27407 | High-test hydrogen peroxide |
| CGA G-4 | Oxygen handling |
| NASA-STD-6001 | Materials flammability and compatibility, which constrains what touches these |
| AIAA S-080 | Metallic pressure vessels, for the tanks the volume split sizes |

---

## Tool interface

```python
from PropellantCombination import PropellantCombination

combination = PropellantCombination()
combination.setInputs({'combination': 'LOX/RP-1', 'areaRatio': 40.0})

density = combination.calculateBulkDensity()
print(density['bulkDensity'], density['fuelVolumeFraction'])

impulse = combination.calculateDensityImpulse()
print(impulse['densityImpulse'])

comparison = combination.compareCombinations()
print(comparison['bySpecificImpulse'][0], comparison['byDensityImpulse'][0])
```

The class refuses a mixture ratio above stoichiometric, and refuses one far below it, because the tabulated chamber temperature and molar mass do not apply in either place.

---

## References

- Sutton and Biblarz, *Rocket Propulsion Elements*, chapter 7
- Gordon and McBride, NASA RP-1311, *Computer Program for Calculation of Complex Chemical Equilibrium Compositions*
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
- Clark, *Ignition! An Informal History of Liquid Rocket Propellants*
- NASA SP-8087, *Liquid rocket engine fluid-cooled combustion chambers*
