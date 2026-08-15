[Home](../README.md) > Validation References

# Validation References

The external sources this sub-domain's tools are checked against, and the several things they cannot check.

Kept separate from the reference lists at the foot of each document. Those are further reading; this is the material a test asserts against. The methodology is in [validation/README.md](../../../validation/README.md).

| Level | Means |
|---|---|
| **Hardware** | Compared against measured or specified performance of real hardware |
| **Standard** | Reproduces a published formula or measurement exactly. Catches an implementation error only |
| **Bounded** | No direct comparison, but the result is bracketed by something |
| **Unvalidated** | No external anchor. Recorded with what depends on it |

**This sub-domain is the least externally anchored in the propulsion tree**, and saying so at the top is more useful than burying it. One source carries almost all of the validation, three of the four classes rest on assumptions registered as unvalidated, and the defensible claims are rankings rather than magnitudes.

---

## The RS-25 start and shutdown sequence

- **Source:** Biggs, *Space Shuttle Main Engine: The First Ten Years*, part 3, Start and Shutdown. Originally presented at the Liquid Rocket Propulsion History Colloquium, AAS Annual Meeting, November 1989; published in *History of Liquid Rocket Engine Development in the United States 1955-1980*, AAS History Series volume 13, pages 69 to 122
- **URL:** <https://enginehistory.org/Rockets/SSME/SSME3.pdf>
- **Accessed:** 09 August 2026
- **Validation level:** Hardware, and it is the only one this sub-domain has
- **Relevance:** The only large liquid engine whose start and shutdown sequences are published to the hundredth of a second. Everything this sub-domain says about sequencing rests on it.
- **Key findings:**
  - Main fuel valve fully open in **0.667 s**, establishing a fuel lead before any oxidiser arrives
  - The three combustors prime at **1.4, 1.5 and 1.6 s**, about a tenth of a second apart
  - Closed loop thrust control at **2.4 s**, closed loop mixture ratio at **3.8 s**, rated power at **5.0 s**
  - A safety check at **1.25 s** requiring the high pressure fuel turbopump above **4600 rpm**, or the engine is shut down, because there would be insufficient time to react later
  - **A timing error of 0.1 s, or a valve position error of 2 per cent and 1 per cent for the oxidiser preburner valve, can lead to significant damage**
  - The high pressure oxidiser turbopump with no fluid load could reach a destructive overspeed in **less than a tenth of a second**, accelerating at about 400,000 rpm per second
  - Shutdown is **open loop**. Oxidiser preburner valve limited to **45 per cent per second**, main oxidiser valve to **40**, the first to satisfy an interface control document limit of **700,000 lbf/s which is an orbiter structural limit**
  - The main fuel valve is held open more than a second to force a fuel-rich shutdown
  - Development cost: 19 tests, 23 weeks and 8 turbopump replacements to reach 2 seconds into a 5 second sequence

**What it validates.** That the sequencing constants in `ignitionUtils` are the published ones, and the sub-domain's central claim about margin: the design prime spacing and the damaging timing error are the same number.

**What it does not validate.** The accumulation model. The source gives no ignition delay and no overpressure, so there is nothing to compare an accumulation calculation against. A start sequence is a schedule; this repository models the accumulation a schedule controls, and the two meet only qualitatively.

---

## Hypergolic ignition delay

- **Source:** Comparative reviews of conventional and green hypergolic propellant ignition delays at ambient conditions, drop test and impinging jet methods
- **Accessed:** 09 August 2026
- **Validation level:** Standard, and weaker than the RS-25 entry above
- **Relevance:** The delay sets the permitted start flow, which is the sub-domain's central design lever.
- **Key findings:**
  - MMH with nitrogen tetroxide at ambient conditions: **1 to 5 ms**, with a commonly cited controlled drop test value near 1.45 ms
  - Liquid phase induction times are **tens of microseconds**, three orders of magnitude below the observed delay
  - The gap between the two is physical transport and heat transfer, which is why the observed delay depends on the injector rather than only on the chemistry
- **Honest limitation:** the primary source was not directly retrievable and these values come from a search summary of it. That is weaker than reading the paper and it is recorded as such.

**Why the weakness does not propagate.** The sub-domain uses the range to bound the permitted start flow, and the competing case, a spark igniter at tens of milliseconds, is an order of magnitude away. Either end of the range gives the same answer to the question being asked.

---

## Cryogen properties

- **Source:** The equation of state, through the repository's shared property wrapper: REFPROP where installed, CoolProp otherwise
- **Validation level:** Standard
- **Relevance:** Every number in the chill-down calculation except the metal specific heat, which comes from the NIST cryogenic material properties curve fits.
- **Key findings:**
  - Latent heat at the normal boiling point: LOX 213 kJ/kg, LCH4 511 kJ/kg, LH2 449 kJ/kg
  - Vapour sensible heat from saturation to 293 K: LOX 187 kJ/kg, LCH4 388 kJ/kg, **LH2 3412 kJ/kg**
  - That last figure is the whole reason hydrogen chill-down is a scheduling problem and oxygen chill-down is not
- **What this means:** nothing in the chill-down capacity calculation is a tabulated value that could go stale, which is deliberate. The tabulated part is the metal, and that is registered as unvalidated below.

---

## Cross-domain consistency

- **Source:** This repository, [combustionDevices](../../combustionDevices/docs/ChamberSizing.md)
- **Validation level:** Internal, and it is a consistency check rather than a validation
- **Key finding:** the chamber residence time computed here, **1.47 ms**, is the same number combustionDevices computes from the same characteristic length and throat area. A test asserts it stays so.
- **Why it is worth having:** a transient calculation and a combustion efficiency calculation turn out to need the same quantity, and if the two ever disagreed one of them would be describing a different chamber.

**It proves nothing about the outside world.** Two parts of one repository agreeing is the weakest form of evidence there is, and the reason this repository has a validation directory at all is that 666 internally consistent tests once failed to catch a placeholder wrong by a factor of three.

---

## What is not validated

Four entries, all registered in [validation/referenceCases.py](../../../validation/referenceCases.py) under `UNVALIDATED`.

**The ignition overpressure bound** (`ignitionOverpressureBound`). Hard start spikes are recorded on test stands and essentially never published with the geometry, flow schedule and ignition delay needed to reconstruct them. The bound assumes everything admitted is at the right mixture ratio, fully vaporised, burns to completion, and burns faster than the nozzle vents. None of those holds, so the absolute spike is an overestimate by an unknown amount. **Only the ranking is claimed**, and the ranking is robust because those four assumptions scale every case identically.

**The igniter energy figures** (`igniterEnergy`). Order of magnitude values with no sourced figure per type. They support one statement, that every device delivers far more than the minimum ignition energy of the mixture, and **no selection depends on them**.

**The tailoff impulse efficiency and its scatter** (`shutdownImpulseScatter`). The residual impulse magnitude moves directly with the first. The conclusion does not: it is that the scatter rather than the magnitude reaches the trajectory, and that holds for any scatter that is not zero.

**The metal specific heats** (`chillDownMeanSpecificHeat`), closed for three metals and open for two.

**Closed:** 304 stainless, 316 stainless and 6061-T6 aluminium now come from the NIST cryogenic material properties curve fits, integrated over the range each chill-down actually traverses rather than tabulated as a mean. The fits reproduce the room-temperature handbook values inside their stated error, and 316 is published as two segments meeting at 50 K which agree there to 0.2 per cent: **that joint is a free check on nine transcribed coefficients and it costs one assertion.**

**Open:** the database carries thermal conductivity and linear expansion for Ti-6Al-4V and Inconel 718 and no specific heat, so those two keep a constant mean over roughly 90 to 300 K. The direction of that approximation is known rather than guessed, because stainless has both routes: a constant quoted over the oxygen range overstates a hydrogen chill-down by 16 per cent, since it never sees the part of the curve below 90 K where specific heat collapses.

**Aluminium 2219 is mapped onto the 6061-T6 curve**, which is a stated approximation and not a measurement. Specific heat per kilogram in a dilute substitutional alloy is set by the base lattice, and the heavier copper 2219 carries means the substitution should run a few per cent high.

---

## The shape of what is left

Reading the four together, the pattern is consistent and worth naming.

**Every magnitude in this sub-domain is weakly anchored and every ranking is strongly anchored.** The overpressure bound cannot say what a spike will be and can say confidently that a hypergolic slug permits ten times the start flow of a spark igniter. The tailoff model cannot say what the cutoff impulse is and can say confidently that the dribble volume dominates the ramp.

The tests are written to that boundary: they assert orderings, ratios and the direction of sensitivities, and they do not assert magnitudes that the sources cannot support.
