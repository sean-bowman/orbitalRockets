[Home](../README.md) > Hazard Zones and Siting

# Hazard Zones and Siting

## Contents

- [Overview](#overview)
- [The two halves](#the-two-halves)
- [The equivalence table](#the-equivalence-table)
- [The hydrogen rule](#the-hydrogen-rule)
- [Cube root scaling](#cube-root-scaling)
- [The K factors](#the-k-factors)
- [Two things reading the standard corrected](#two-things-reading-the-standard-corrected)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

How far away everything has to be. This is the one part of ground systems with a hard published standard behind it, and the standard was read in full rather than summarised.

---

## The two halves

Siting a pad is two calculations in sequence and they fail differently.

**Convert the propellant into an equivalent weight of TNT.** This is a table lookup with one important exception, and the exception is hydrogen.

**Scale that weight into a distance.** This is Hopkinson-Cranz cube-root scaling with a K factor chosen from the consequence being designed against.

The first half is where the judgement is and the second half is arithmetic.

---

## The equivalence table

DESR 6055.09 Table V5.E4.T5, reproduced as NASA-STD-8719.12A Table 5-29. Percentages are of the total propellant mass, oxidiser and fuel together, aboveground and unconfined except by its own tankage.

| Combination | Range launch | Static test stand |
|---|---|---|
| LO2/RP-1 | 20% up to 226,795 kg, 10% above | 10% |
| LO2/LH2 | see [the hydrogen rule](#the-hydrogen-rule) | same |
| IRFNA/UDMH | 10% | 10% |
| N2O4/UDMH + N2H4 | 10% | 5% |
| N2O4 with PBAN, hybrid | 15% | 15% |
| Nitromethane | 100% | 100% |

**The static test stand column is never higher**, because a stand can be built to keep the propellants apart in a way a vehicle cannot. MMH substitutes for hydrazine or UDMH, and alcohols or other hydrocarbons substitute for RP-1.

**A combination not in the table goes to individual assessment**, and the library refuses rather than defaulting. Methane is the notable absence: it is a current propellant with no entry, and the [interim LO2/LNG work](StandardsIndex.md) is exactly that, interim.

---

## The hydrogen rule

The interesting one, and the reason this document exists.

```
W_TNT = max( 8 * W ** (2/3),  0.14 * W )      W in pounds
```

The two terms are equal at **186,589 lb, which is 84,635 kg**. Above that the flat fourteen per cent governs. Below it the sublinear term governs, and the effective fraction rises as the load falls:

| LO2/LH2 load | Effective fraction | Governing |
|---|---|---|
| 4,232 kg | 38.0% | sublinear |
| 16,927 kg | 23.9% | sublinear |
| 42,318 kg | 17.6% | sublinear |
| 84,635 kg | 14.0% | crossover |
| 169,271 kg | 14.0% | flat |
| 423,177 kg | 14.0% | flat |

**A small hydrogen stage is disproportionately hazardous per kilogram.** That reverses the intuition that a small vehicle is a small siting problem, and it means a modest upper stage can drive a pad layout its propellant mass would not suggest.

The physical reading is that a small spill mixes more completely before it ignites. A large one does not: most of it is still liquid when the first of it detonates.

---

## Cube root scaling

```
d = K * W ** (1/3)      d in feet, W in pounds of TNT equivalent
```

The scaling is a similarity law rather than a convention. Two charges of the same explosive produce the same overpressure at the same scaled distance, so one set of K factors covers every quantity.

**It runs the wrong way for fixing a shortfall.** Eight times the propellant is twice the distance, so halving a required distance means cutting the load by a factor of eight, and no vehicle offloads that much. **A facility that fails its siting has to move, or the operation has to change.**

The same compression works in your favour when comparing propellants. A factor of ten in equivalent weight is a factor of 2.15 in distance.

---

## The K factors

NASA-STD-8719.12A Table E-1, read in full. The overpressures are the part that almost never travels with the K values in secondary sources, and they are what makes the table intelligible.

| K | psi | Means |
|---|---|---|
| 1.79 | 386.9 | lethality from lung rupture |
| 3.33 | 107.1 | lethality from lung rupture |
| 3.90 | 74.4 | 99% chance of eardrum rupture |
| 6 | 27.0 | barricaded intermagazine distance |
| 8 | 15.0 | 50% chance of eardrum rupture |
| 9 | 12.0 | intraline distance, barricaded |
| 11 | 8.0 | intermagazine distance, unbarricaded |
| 18 | 3.5 | intraline distance, unbarricaded |
| 24 | 2.3 | public traffic route |
| 30 | 1.7 | public traffic route, large quantities |
| 40 | 1.2 | inhabited building distance |
| 50 | 0.9 | inhabited building distance, relaxed |

**Inhabited building distance is K = 40 and 1.2 psi.** At that level an unstrengthened building sustains damage of about five per cent of its replacement cost, and injuries are principally from glass and debris rather than from blast.

**These model overpressure only.** Fragmentation and thermal effects are separate criteria and can govern instead, which the standard says explicitly and which a K factor calculation cannot tell you.

---

## Two things reading the standard corrected

Both are the kind of thing a summary loses, and both are recorded in [ValidationReferences](ValidationReferences.md).

**The sixty per cent figure is not the siting rule.** The commonly quoted 60 per cent TNT equivalence for LO2/LH2 comes from the Project PYRO test series of the 1960s and from an evaluation of shuttle on-pad operations. It is a yield figure. **The siting rule is the max of the sublinear and flat terms**, and building a library on 60 per cent would have overstated a small stage by about a factor of three while missing the shape of the rule entirely.

**The standard's own metric coefficient does not convert.** The rule is printed as `8 W**(2/3)` with W in pounds and, in brackets, `4.13 Q**(2/3)` with Q in kilograms. **Those are not the same rule.** Converting the English form exactly gives 6.147, and the two differ by a factor of 1.488 with the published metric form the smaller.

An analyst working natively in SI from the bracketed coefficient gets a shorter siting distance than the form the table is built on, which is a non-conservative error rather than a rounding one. The discrepancy is present in both DESR 6055.09 Edition 1 Change 1 and NASA-STD-8719.12A. **This library computes in the English form and converts**, and a test asserts the discrepancy rather than quietly correcting it.

---

## Worked numbers

A two stage vehicle: 270 t of LO2/RP-1 and 38 t of LO2/LH2.

| Quantity | Value |
|---|---|
| First stage equivalent | 49,680 kg, 18.4% |
| Second stage equivalent | 6,948 kg, 18.3% |
| Second stage read as a flat 14% | 5,320 kg, understated by 31% |
| Combined equivalent | 56,628 kg |
| Inhabited building distance | 609 m |
| Public traffic route | 366 m |
| Intraline, unbarricaded | 274 m |

**The two stages come out at almost the same effective fraction despite a factor of seven in mass**, which is the hydrogen rule doing its work: the kerosene stage is above its own break mass and being reduced, the hydrogen stage is below its crossover and being raised.

---

## Design rules of thumb

- **Read the standard, not a summary of it.** Both corrections above came from doing that.
- **Site on the whole quantity subject to mixing**, which is what the standard asks for, not on what would burn.
- **Check where a hydrogen load sits against 84,635 kg** before assuming fourteen per cent.
- **Do not expect to fix a siting shortfall by offloading.** Cube root scaling will not let you.
- **Remember that K factors are overpressure only.** Fragments and thermal are separate and can govern.

---

## Failure modes

**Sixty per cent used as a siting equivalence.** A test yield figure, not the rule.

**The bracketed metric coefficient used natively.** A shorter distance than the standard intends.

**A combination not in the table given a plausible percentage.** The standard sends it to assessment for a reason.

**Fragmentation ignored.** It can govern and the K factors say nothing about it.

**The binding facility assumed to be the closest one.** It is the one whose criterion is strictest relative to where it sits.

---

## Tool interface

```python
from HazardSiting import HazardSiting

siting = HazardSiting()
siting.setInputs({'combination':     'LO2/RP-1',
                  'propellantMass':  270000.0,
                  'additionalLoads': {'LO2/LH2': 38000.0},
                  'facilities': [{'name': 'launch control', 'distance': 4500.0,
                                  'criterion': 'inhabitedBuilding'}]})

equivalent = siting.calculateEquivalent()
rings      = siting.calculateDistances()
check      = siting.checkFacilities()      # raises if a facility is inside its ring
crossover  = siting.hydrogenCrossover()
```

`checkFacilities` raises rather than reporting a negative margin, because a control room inside inhabited building distance is not a design with a small shortfall in it.

---

## References

- DESR 6055.09, *Defense Explosives Safety Regulation*, Edition 1 Change 1, Volume 5 Enclosure 4, Table V5.E4.T5 and footnote f
- NASA-STD-8719.12A, *Safety Standard for Explosives, Propellants and Pyrotechnics*, Tables 5-29 and E-1
- AFRPL-TR-67-124, for the hybrid propellant evaluation cited in the standard
- Project PYRO, the 1960s test series behind the yield figures
- [ValidationReferences](ValidationReferences.md)
