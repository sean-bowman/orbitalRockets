[Home](../../README.md) > Materials Compatibility

# Materials Compatibility

## Contents

- [Overview](#overview)
- [The compatibility matrix](#the-compatibility-matrix)
- [Oxygen compatibility](#oxygen-compatibility)
- [Hydrogen embrittlement](#hydrogen-embrittlement)
- [Hydrazine and copper](#hydrazine-and-copper)
- [Nitrogen tetroxide](#nitrogen-tetroxide)
- [Hydrogen peroxide](#hydrogen-peroxide)
- [Elastomer selection](#elastomer-selection)
- [Galvanic and stress corrosion](#galvanic-and-stress-corrosion)
- [Lubricants](#lubricants)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Materials compatibility is where fluid system design stops being about pressure drop and starts being about whether the hardware survives contact with what is inside it.

Most compatibility questions have a boring answer: 316L stainless is compatible with almost everything a propulsion system contains, and if you build the whole system out of it you will mostly be fine. The interesting cases are the ones where a material that is obviously suitable on every other axis is catastrophically wrong:

| Combination | Why it is wrong |
|---|---|
| **Titanium in LOX or GOX** | Impact sensitive. It burns |
| **Copper alloys in hydrazine** | Catalyze decomposition |
| **Aluminum in N2O4 above 60 degC** | Rapid corrosion |
| **Buna-N in hydrazine** | Degrades, and catalyzes decomposition |
| **High strength steel in hydrogen** | Embrittles and cracks |
| **Any hydrocarbon in oxygen** | Ignition source |

Every one of these has destroyed hardware, and several have killed people. The [`Fitting.checkCompatibility`](../Fitting.py) and [`Seal.checkCompatibility`](../Seal.py) methods raise `CompatibilityError` on these rather than warning, deliberately: they should not be lines you can scroll past.

---

## The compatibility matrix

**Metals:**

| Material | LOX/GOX | LH2/GH2 | N2H4 | MMH | N2O4 | RP-1 | H2O2 | LN2/GN2 | He |
|---|---|---|---|---|---|---|---|---|---|
| **304L / 316L** | ok | ok | **ok** | ok | ok | ok | ok | ok | ok |
| 321 / 347 | ok | ok | ok | ok | ok | ok | ok | ok | ok |
| 17-4 PH | ok | **caution** | ok | ok | ok | ok | caution | ok | ok |
| **6061 / 2219 Al** | ok | ok | **ok** | ok | **NO >60C** | ok | caution | ok | ok |
| 7075 | ok | ok | ok | ok | no | ok | no | ok | ok |
| **Ti-6Al-4V** | **NEVER** | **caution** | ok | ok | **NO** | ok | no | ok | ok |
| Inconel 718 | ok | ok | ok | ok | ok | ok | ok | ok | ok |
| Inconel 625 | ok | ok | ok | ok | ok | ok | ok | ok | ok |
| **Monel 400** | ok | ok | **NO** | no | ok | ok | **ok** | ok | ok |
| **Copper, brass, bronze** | caution | ok | **NO** | **NO** | no | ok | **NO** | ok | ok |
| Nickel | ok | ok | caution | caution | ok | ok | ok | ok | ok |
| Silver | caution | ok | caution | caution | ok | ok | **NO** | ok | ok |
| **Carbon steel** | no | **NO** | no | no | no | ok | **NO** | no (cryo) | ok |
| Magnesium, zinc, cadmium | no | ok | **NO** | no | no | ok | no | ok | ok |

**Polymers and elastomers:**

| Material | LOX/GOX | LH2 | N2H4 | MMH | N2O4 | RP-1 | H2O2 | Cryo |
|---|---|---|---|---|---|---|---|---|
| **PTFE** | ok | ok | ok | ok | ok | ok | ok | ok (contracts) |
| **PCTFE (Kel-F)** | **ok** | ok | ok | ok | ok | ok | ok | **ok** |
| **FKM (Viton)** | no | no | **NO** | no | **ok** | ok | no | no (Tg 255 K) |
| **EPDM** | no | no | **ok** | **ok** | no | **NO** | ok | no (Tg 218 K) |
| **NBR (Buna-N)** | no | no | **NO** | **NO** | no | **ok** | no | no |
| Butyl (IIR) | no | no | ok | ok | no | no | ok | no |
| Silicone | no | no | no | no | no | no | no | marginal |
| FFKM (Kalrez) | no | no | ok | ok | ok | ok | ok | no (Tg 264 K) |
| Vespel (polyimide) | caution | ok | ok | ok | ok | ok | caution | ok |
| PEEK | caution | ok | ok | ok | ok | ok | ok | ok |

---

## Oxygen compatibility

Oxygen does not burn. It makes everything else burn, and materials that are perfectly inert in air become fuels in an oxygen-enriched environment.

**Three ignition mechanisms, all of which have caused accidents:**

1. **Particle impact.** A particle entrained in a high-velocity oxygen stream impacts a wall or a fitting transition, converts its kinetic energy into local heating, and ignites. The particle then ignites the substrate. This is why the LOX and GOX velocity limits exist and why they are hard limits rather than guidance.
2. **Adiabatic compression.** Rapid pressurization of a dead-ended volume heats the trapped gas. Compressing GOX from 1 atm to 20 MPa reaches about 1330 K, above the ignition temperature of every non-metal and of aluminum. See [WaterHammer.md](WaterHammer.md).
3. **Mechanical impact and friction.** A valve slamming shut, a component impacting another, or rubbing contact. This is what LOX mechanical impact testing (NASA-STD-6001 Test 13, ASTM G86) evaluates.

**Autoignition temperatures in oxygen** (indicative; they fall with pressure and with contamination):

| Material | Ignition temperature |
|---|---|
| Hydrocarbon oil or grease | ~500 K |
| FKM (Viton) | ~590 K |
| PCTFE (Kel-F) | ~660 K |
| PTFE | ~780 K |
| Aluminum | ~1000 K |
| Carbon steel | ~1600 K |
| **316 stainless** | **~1700 K** |
| **Monel** | **~2200 K** |
| Copper | ~2200 K |

**Material ranking for oxygen service**, best to worst: Monel, copper alloys, nickel, 316 stainless, Inconel, carbon steel, aluminum, titanium (never).

Note that **copper and Monel are the best metals for oxygen service** even though copper is prohibited in hydrazine. Compatibility is fluid-specific and there is no universal "good" material.

**Titanium in oxygen is a hard prohibition.** Titanium is impact sensitive in both liquid and gaseous oxygen, it burns readily once ignited, and the combustion is self-sustaining. There is no design mitigation. It is also prohibited in red fuming nitric acid and in N2O4.

**Design practice for oxygen systems:**

- Velocity limits: 7.6 m/s for LOX (12.2 m/s only with verified cleanliness and no soft goods), 30 m/s for GOX in carbon steel
- No dead-ended volumes downstream of fast valves
- Slow valve opening, at a defined rate
- **No hydrocarbon lubricants anywhere.** Only approved perfluorinated products (Krytox, Fomblin), applied sparingly and documented
- Cleanliness to ASTM G93 Level or better; see [CleanlinessAndContamination.md](CleanlinessAndContamination.md)
- Impingement sites (elbows, tees, valve seats) get the most ignition-resistant materials
- All soft goods qualified by LOX mechanical impact testing at the design pressure

---

## Hydrogen embrittlement

Hydrogen dissolves into metals atomically, diffuses to regions of high triaxial stress (crack tips, notches, inclusions), and reduces the local cohesive strength. The result is delayed, brittle fracture at stresses well below the yield strength.

**Susceptibility ranking:**

| Material class | Susceptibility |
|---|---|
| **High strength steels (> 1000 MPa UTS)** | **Severe.** Essentially unusable in hydrogen |
| Martensitic and precipitation hardened steels | Severe |
| Ferritic steels | High |
| **Ti-6Al-4V** | High, particularly at elevated temperature |
| Inconel 718 | Moderate. Better than most superalloys, not immune |
| Nickel and high-nickel alloys | Moderate |
| **304L, 316L austenitic stainless** | **Low.** The FCC lattice resists it |
| **6061, 2219 aluminum** | **Very low.** Aluminum is effectively immune |
| Copper | Very low |

**Three factors control the severity:**

1. **Strength.** Susceptibility rises steeply with strength. This is the dominant factor and it is why high strength steels are unusable.
2. **Microstructure.** FCC lattices (austenitic stainless, aluminum, copper) resist because hydrogen diffuses slowly through them and they have many slip systems. BCC and martensitic structures are susceptible.
3. **Stress state.** Hydrogen accumulates where the hydrostatic tension is highest. Notches, weld toes, thread roots and crack tips are all concentrators.

**Design practice for hydrogen systems:**

- 316L stainless or aluminum for everything in contact with hydrogen
- Keep strength moderate; a lower strength alloy at greater wall thickness is the right trade
- Minimize stress concentrations: full penetration welds, generous radii, no sharp thread roots
- Avoid cold work, which raises the local strength and the residual stress
- Bake out after any process that could charge hydrogen (electroplating, acid pickling)
- ASME B31.12 governs hydrogen piping and it carries specific material and design factors

**Hydrogen also permeates.** It is the smallest molecule and it goes through elastomers faster than any other gas, and through some metals at elevated temperature. A long-life hydrogen system has a permeation loss budget as well as a leak budget.

---

## Hydrazine and copper

**Copper and copper-bearing alloys catalyze hydrazine decomposition.** So do iron oxide, molybdenum, cobalt and, less strongly, silver and nickel.

The consequence is not corrosion. It is **gas generation inside the fluid system**, upstream of the injector, which causes:

- Flow instability and injector maldistribution
- An unexplained slow rise in tank pressure in a blowdown system
- In a trapped volume, an unbounded pressure rise

**The prohibition covers more than obvious copper:**

| Prohibited | Why it is easy to miss |
|---|---|
| Brass fittings | Standard plumbing hardware |
| Bronze bushings | Inside purchased valves and regulators |
| **Monel** | A nickel-copper alloy; excellent for oxygen and prohibited here |
| Copper-based anti-seize | Standard shop consumable |
| Copper sulfate passivation verification | **The verification test deposits copper.** See [Passivation.md](Passivation.md) |
| Copper gaskets | ConFlat seals |
| Brazed joints with copper filler | |

**Acceptable materials:** 300-series stainless, 6061 and 2219 aluminum, titanium, Inconel 625 and
718. Nickel is marginal and acceptable as a thin plating in small areas.

---

## Nitrogen tetroxide

N2O4 (and its inhibited variants MON-1 and MON-3, which contain 1 to 3 percent nitric oxide) is corrosive in a way that depends critically on water content and on temperature.

**Water is the problem.** N2O4 reacts with water to form nitric acid, and nitric acid attacks everything. Anhydrous N2O4 in a dry system is manageable; the same fluid with 0.5 percent water is aggressive.

| Material | N2O4 compatibility |
|---|---|
| **304L, 316L, 321 stainless** | Good |
| **Ti-6Al-4V** | **Stress corrosion cracks** in uninhibited N2O4. The reason MON grades exist |
| **6061 aluminum** | Good below 60 degC, rapid attack above |
| Inconel | Good |
| **FKM (Viton)** | The standard elastomer for N2O4 |
| EPDM, NBR, butyl | Attacked |
| PTFE, PCTFE | Good |

**The titanium SCC story is worth knowing.** Early N2O4 tanks in titanium cracked in service. The cause was traced to stress corrosion cracking in uninhibited N2O4, and the fix was to add 0.6 to 1.0 percent nitric oxide, which produces **MON-1** and inhibits the cracking. MON-3 (3 percent NO) is used where a lower freezing point is needed. Even so, titanium in N2O4 is a case that requires specific qualification rather than a general acceptance.

---

## Hydrogen peroxide

High-test peroxide decomposes catalytically on almost any contaminated surface. Compatibility is therefore about **catalytic activity** rather than about corrosion.

| Class | Materials |
|---|---|
| **Class 1 (best)** | Passivated 5254 and 1060 aluminum, high purity aluminum, PTFE, PCTFE, glass |
| **Class 2** | Passivated 300-series stainless, tin, some polymers |
| **Class 3** | Materials acceptable for short exposure only |
| **Class 4 (prohibited)** | Copper, silver, iron, brass, most elastomers, any organic contamination |

Note that **300-series stainless is Class 2, not Class 1**, for peroxide. That is the opposite of essentially every other propellant in this document, and it is why HTP systems are built in aluminum.

**Peroxide systems must be passivated to the propellant** by successive rinses of increasing concentration, and the system is considered passivated when the measured decomposition rate falls below a specified value. That is a functional test, not a procedural step. See [Passivation.md](Passivation.md).

**Every peroxide system needs a vent path.** The propellant decomposes slowly even in a clean system, and a sealed container will pressurize.

---

## Elastomer selection

| Propellant | Use | Never use |
|---|---|---|
| **Hydrazine, MMH** | EPDM, butyl, PTFE, PCTFE, FFKM | **NBR, FKM**, silicone, polyurethane |
| **N2O4** | **FKM**, PTFE, PCTFE, FFKM | EPDM, NBR, butyl, silicone |
| **RP-1, hydrocarbons** | **NBR**, FKM, PTFE | EPDM, butyl |
| **LOX, GOX** | **PCTFE**, PTFE (both qualified by impact test) | Every elastomer |
| **Cryogenic (any)** | PCTFE, spring-energized PTFE, metal seals | Every elastomer (all are below Tg) |
| GN2, GHe, air | Almost anything; select on temperature and permeation | -- |

**Note the direct conflict between hydrazine and N2O4.** EPDM is right for the fuel and wrong for the oxidizer; FKM is the reverse. A bipropellant system therefore uses **different seal materials on the two sides**, which is a configuration control problem: two o-rings of the same size in different materials are indistinguishable by eye. **Control seals by part number, never by dimension.**

Full seal material data, including glass transition temperatures and permeability, is in [Seals.md](Seals.md).

---

## Galvanic and stress corrosion

**Galvanic corrosion** requires three things: two dissimilar metals, electrical continuity, and an electrolyte. A launch site provides the electrolyte (salt fog) for free.

The galvanic series, most anodic (sacrificial) to most cathodic:

```
magnesium -> zinc -> aluminum -> cadmium -> carbon steel -> cast iron -> 304/316 (active) ->
lead -> tin -> nickel -> brass -> copper -> bronze -> Monel -> silver -> titanium ->
316 (passive) -> graphite -> gold, platinum
```

The further apart two materials are, the worse the couple, and **the anodic member corrodes at a rate proportional to the cathode area**. A small aluminum fitting in a large stainless system corrodes fast; a small stainless fitting in a large aluminum system barely affects it.

Mitigations: avoid the couple, isolate electrically, coat the cathode (not the anode), or accept and inspect.

**Stress corrosion cracking** requires a susceptible material, a sustained tensile stress, and a specific environment. The classic aerospace cases:

| Material | Environment | Note |
|---|---|---|
| **300-series austenitic stainless** | **Chlorides** above about 60 degC | Salt fog plus residual weld stress plus warm |
| **7000-series aluminum** | Moisture, particularly short transverse | Why 7075-T73 exists rather than T6 |
| **Titanium** | **Uninhibited N2O4**, methanol, red fuming nitric acid | See above |
| High strength steels | Hydrogen, H2S | |

The residual tensile stress from welding is often what turns a benign situation into an SCC case. See [Welds.md](Welds.md).

---

## Lubricants

Every lubricant is a contaminant somewhere. The rule is to use as little as possible, of an approved product, documented.

| Lubricant | Oxygen | Hydrazine | Cryogenic | Note |
|---|---|---|---|---|
| **Krytox (PFPE)** | **ok** | ok | ok | The oxygen standard. Perfluorinated, non-flammable in oxygen |
| Fomblin (PFPE) | ok | ok | ok | Equivalent |
| Braycote (PFPE grease) | ok | ok | ok | Vacuum and cryogenic standard |
| **Hydrocarbon oils and greases** | **NEVER** | no | no | Ignition source in oxygen |
| Silicone grease | no | no | marginal | Migrates, contaminates optical and bonded surfaces |
| **MoS2 dry film** | no | ok | ok | Good for threads; not for oxygen |
| Copper anti-seize | ok | **NEVER** | ok | Copper catalyzes hydrazine |
| Nickel anti-seize | caution | marginal | ok | Nickel is mildly catalytic in hydrazine |
| **Silver plating** | caution | marginal | ok | Standard on flare nuts; mildly catalytic |

---

## Design rules of thumb

| Rule | Value | Why |
|---|---|---|
| Default material | 316L stainless | Compatible with almost everything |
| Titanium in oxygen | **Never** | Impact sensitive, burns |
| Copper alloys in hydrazine | **Never** | Catalyzes decomposition |
| Hydrocarbon lubricant in oxygen | **Never** | Ignition source |
| High strength steel in hydrogen | Never | Embrittlement |
| Hydrogen systems | 316L or aluminum, moderate strength | FCC resists embrittlement |
| N2O4 with titanium | Only with MON inhibition, and qualify it | SCC |
| Aluminum in N2O4 | Below 60 degC only | Rapid attack above |
| HTP systems | Aluminum, not stainless | Catalytic activity, not corrosion |
| Bipropellant seals | Different material each side | EPDM fuel, FKM oxidizer |
| Seal control | By part number, never dimension | Same size, different material, invisible |
| Galvanic couple | Small anode in large cathode is worst | Area ratio drives the rate |
| Every peroxide system | Vent path | It decomposes in storage |

---

## Failure modes

**Titanium fire in an oxygen system.** Total and immediate.

**Hydrazine decomposition from a copper fitting.** Gas in the feed line, unexplained pressure rise, and in a trapped volume an unbounded pressure.

**Delayed hydrogen embrittlement fracture.** Hours to weeks after loading, at a stress well below yield, with no deformation.

**Chloride SCC of a stainless weld.** Cracking at the weld toe, months after fabrication, driven by salt fog plus residual stress.

**Elastomer swell.** An incompatible seal swells, extrudes, and sheds material into the propellant. In hydrazine the shed material then poisons the catalyst.

**Elastomer of the right size and wrong material.** Installed because it fit. The single most common configuration control failure in seal work.

**Aluminum corrosion in warm N2O4.** Rapid, and it accelerates as the corrosion products catalyze further attack.

**Peroxide runaway decomposition.** From contamination, in a sealed volume. The system pressurizes to burst.

**Galvanic corrosion at a dissimilar metal joint.** Discovered at teardown, or when the joint leaks.

**Lubricant contamination.** Hydrocarbon grease in an oxygen system, or copper anti-seize in a hydrazine system. Both introduced by someone doing routine maintenance with what was on the shelf.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-6001** | Flammability, offgassing and compatibility requirements and test procedures. Test 13 is LOX mechanical impact |
| **ASTM G88** | Designing systems for oxygen service |
| ASTM G63 | Evaluating nonmetallic materials for oxygen service |
| ASTM G94 | Evaluating metals for oxygen service |
| ASTM G86 | Determining ignition sensitivity of materials to mechanical impact in oxygen |
| ASTM G72 | Autogenous ignition temperature of materials in oxygen |
| ASTM G93 | Cleaning methods and cleanliness levels for oxygen service |
| **ASME B31.12** | Hydrogen piping and pipelines |
| ANSI/AIAA G-095 | Guide to safety of hydrogen and hydrogen systems |
| **NASA/TM-2016-219078** | Safety standard for hydrogen and hydrogen systems |
| ASTM F519 | Mechanical hydrogen embrittlement evaluation of plating processes |
| MIL-STD-1246 | Product cleanliness levels (superseded by IEST-STD-CC1246) |
| CPIA/JANNAF | Chemical propulsion hazards manuals |
| MIL-PRF-26536 | Hydrazine specification |
| MIL-PRF-26539 | Nitrogen tetroxide specification |
| MIL-PRF-16005 | Hydrogen peroxide specification |
| ASTM G82 | Development and use of a galvanic series |

---

## Tool interface

Compatibility screening is built into the component classes and raises rather than warns:

```python
from Fitting import Fitting, INCOMPATIBLE_COMBINATIONS
from Seal import Seal, SEAL_MATERIALS
from utils import materialProperties, CompatibilityError

# Fitting body material against the service fluid
fitting = Fitting()
fitting.setInputs({'fittingType': 'an flare', 'tubeOuterDiameter': 0.00635,
                   'material': 'TI-6AL-4V', 'fluid': 'LOX',
                   'designPressure': 5.0e6})
try:
    fitting.checkCompatibility()
except CompatibilityError as error:
    print(error)     # titanium in LOX is a hard stop

# Seal material against fluid, temperature and glass transition
seal = Seal()
seal.setInputs({'material': 'nbr', 'crossSectionDiameter': 0.00178,
                'fluid': 'N2H4', 'designPressure': 2.5e6})
seal.checkCompatibility()    # raises: NBR in hydrazine

# Material properties with the cryogenic strength correction and the compatibility note
properties = materialProperties('TI-6AL-4V', 90.0)
print(properties['notes'])   # the LOX prohibition is in the note
```

Lookup tables: `Fitting.INCOMPATIBLE_COMBINATIONS`, `Seal.SEAL_MATERIALS` (with `compatible` and `incompatible` lists per material), `utils.materialProperties` (with a `notes` field carrying the governing caution for each alloy).

---

## References

1. NASA-STD-6001B, *Flammability, Offgassing, and Compatibility Requirements and Test Procedures*.
2. ASTM G88-13, *Standard Guide for Designing Systems for Oxygen Service*.
3. Beeson, H. and Woods, S., *Guide for Oxygen Compatibility Assessments on Oxygen Components and Systems*, NASA/TM-2007-213740.
4. ANSI/AIAA G-095A-2017, *Guide to Safety of Hydrogen and Hydrogen Systems*.
5. Schmidt, E. W., *Hydrazine and Its Derivatives*, 2nd ed., Wiley, 2001.
6. Clark, J. D., *Ignition!*, Rutgers University Press, 1972.
7. Sutton, G. P. and Biblarz, O., *Rocket Propulsion Elements*, 9th ed., Wiley, 2016.
8. ASM Handbook Volume 13, *Corrosion*, ASM International.
9. Ventura, M. and Wernimont, E., "History of the Reinvention of Hydrogen Peroxide Based Propulsion", AIAA 2001-3838.
