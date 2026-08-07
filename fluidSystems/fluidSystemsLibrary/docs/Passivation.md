[Home](../../README.md) > Passivation

# Passivation

## Contents

- [Overview](#overview)
- [What passivation actually is](#what-passivation-actually-is)
- [Processes](#processes)
- [Process selection](#process-selection)
- [Verification](#verification)
- [Passivation of other alloys](#passivation-of-other-alloys)
- [Propellant passivation: a different meaning](#propellant-passivation-a-different-meaning)
- [Spacecraft passivation: a third meaning](#spacecraft-passivation-a-third-meaning)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Operations](#operations)
- [Standards](#standards)
- [References](#references)

---

## Overview

The word "passivation" means three different things in an aerospace fluid system context, and confusing them causes real problems in specifications:

| Meaning | What it is | Where it appears |
|---|---|---|
| **Chemical passivation** | Removing free iron from a stainless surface and restoring the chromium oxide film | Manufacturing, cleaning, part specifications |
| **Propellant passivation** | Conditioning a system to its service propellant so it stops reacting with it | Fluorine, N2O4, hydrogen peroxide systems |
| **Spacecraft passivation** | Depleting stored energy at end of mission | Orbital debris mitigation requirements |

This document covers all three, with the emphasis on the first, which is the one that appears on every stainless steel part drawing.

---

## What passivation actually is

Austenitic stainless steel is corrosion resistant because chromium in the alloy forms a thin, adherent, self-healing chromium oxide film on the surface. That film is what makes the steel "stainless"; the bulk alloy underneath is not intrinsically corrosion resistant.

**Two things break the film:**

1. **Free iron on the surface.** Machining, grinding, forming, or contact with carbon steel tooling smears iron particles onto the surface. That iron is not protected by the chromium film, it rusts, and the rust breaks down the adjacent film. A single carbon steel chip embedded in a stainless surface will bloom into a rust spot and undermine the passive layer around it.
2. **Chromium depletion.** Welding, heat treatment, or any excursion through 700 to 1150 K precipitates chromium carbides at grain boundaries and locally depletes the adjacent metal of chromium. That is sensitization, and it is covered in [Welds.md](Welds.md).

**Passivation addresses the first.** It is an acid treatment that:

- **Dissolves free iron and other exogenous metallic contamination** from the surface, preferentially over the base alloy
- **Promotes reformation of the chromium oxide film**, either by allowing it to reform in air after cleaning or by actively oxidizing the surface in a nitric acid bath

**Passivation is not cleaning.** It removes metallic contamination, not organic contamination. Degreasing must happen first, and if it does not, the oils shield the surface from the acid and the passivation is worthless. A part that arrives at the passivation tank with fingerprints on it comes out with passivated areas and unpassivated fingerprints.

**Passivation is not a coating.** Nothing is added. The film is a few nanometres of chromium oxide that would have formed anyway in air; the acid treatment removes what was preventing it.

---

## Processes

### Nitric acid

The traditional process. Nitric acid dissolves free iron and simultaneously oxidizes the surface, which accelerates chromium oxide formation.

| Bath | Composition | Temperature | Time | Use |
|---|---|---|---|---|
| Nitric 1 | 20 to 25 vol % HNO3, 2.5 wt% sodium dichromate | 322 to 336 K | 20 min | 400 series, high carbon martensitic |
| Nitric 2 | 20 to 45 vol % HNO3 | 294 to 322 K | 30 min | 300 series (302, 303, 304), free machining grades |
| **Nitric 3** | **20 to 45 vol % HNO3** | **322 to 336 K** | **20 min** | **300 series general, the common choice** |
| Nitric 4 | 20 to 50 vol % HNO3 | 294 to 322 K | 30 min | 300 series, precipitation hardening |
| Nitric 5 | 20 to 25 vol % HNO3, 2.5 wt% sodium dichromate | 322 to 336 K | 20 min | Free machining, high sulfur grades |

(Bath designations per ASTM A967.)

**Sodium dichromate** is added for grades that are attacked by plain nitric acid: free-machining grades with high sulfur, and martensitic grades. It is a hexavalent chromium compound, which is a serious health and environmental hazard, and there is strong regulatory pressure to eliminate it.

**Drawbacks of nitric acid:**

- Hazardous waste stream, and nitrate discharge is regulated
- Hexavalent chromium in the dichromate baths
- NOx fumes
- Can attack some grades and some weld metals if the concentration or temperature is wrong

### Citric acid

The modern alternative and, increasingly, the default. Citric acid chelates iron: it forms a soluble complex with iron ions and carries them away, without the strong oxidizing action of nitric acid.

| Parameter | Typical |
|---|---|
| Concentration | 4 to 10 wt % citric acid |
| Temperature | 322 to 350 K |
| Time | 10 to 30 min |
| pH adjustment | Often to 1.8 to 2.2 with an inhibitor package |

**Advantages:**

- Non-hazardous waste stream; citric acid is a food additive
- No hexavalent chromium
- No NOx
- Less aggressive to the base metal, so less risk of over-etching a weld or a fine feature
- Works on a wider range of alloys including some that nitric attacks

**Considerations:**

- The chromium oxide film forms in air after the treatment rather than being driven by the bath, so the part must be rinsed, dried and given time (typically 24 to 48 hours) before the passive layer is fully developed
- Proprietary formulations vary considerably; qualify the specific product
- Slightly less effective at removing heavy embedded iron, so surface preparation matters more

**For aerospace fluid system hardware, citric acid passivation per ASTM A967 or AMS 2700 Method 2 is now the usual choice**, and it is preferred wherever the waste stream or hexavalent chromium is a consideration, which is essentially everywhere.

### Electropolishing

Not strictly passivation, but it achieves the same end and more. An electrochemical process that preferentially removes the high points of a surface, producing:

- A very smooth surface (Ra improved by a factor of 2 to 5)
- Preferential removal of iron relative to chromium, leaving a **chromium-enriched surface**
- No embedded contamination, because material is removed rather than treated
- A deburred surface, including internal features that cannot be reached mechanically

**Electropolishing produces a better passive layer than any acid passivation**, with a higher chromium-to-iron ratio at the surface. It is the standard for ultra-high-purity gas systems, semiconductor process gas lines, and anywhere the surface itself is a contamination source.

Costs: more expensive, requires an electrical connection to every part (which leaves a contact mark), removes material (so dimensions change), and rounds sharp edges, which may or may not be acceptable.

---

## Process selection

| Situation | Process |
|---|---|
| General 300-series fluid system hardware | **Citric acid, ASTM A967 or AMS 2700 Method 2** |
| Legacy specification calls for nitric | Nitric 3 for 300 series |
| Free machining grades (303, 416) | Nitric with dichromate, or a qualified citric formulation |
| Martensitic and precipitation hardening (410, 17-4 PH) | Nitric per the appropriate bath, verify no hydrogen embrittlement |
| Ultra-high-purity gas, semiconductor, high vacuum | **Electropolish** |
| Internal surfaces of small-bore tubing | Electropolish, or circulate the passivation solution |
| Oxygen service | Passivate, then clean to the oxygen cleanliness level. **The passivation comes first** |
| After welding | Passivate after all welding and grinding is complete, never before |

**Sequence matters and it is frequently got wrong:**

```
machine  ->  weld  ->  grind/blend  ->  DEGREASE  ->  PASSIVATE  ->  rinse  ->  dry  ->
             final clean to the cleanliness level  ->  package
```

Passivating before welding is pointless: the weld destroys the film locally and adds heat tint (an oxide scale that must itself be removed). Passivating before final grinding is equally pointless. **Passivation is one of the last operations, and it precedes only the final cleanliness cleaning and packaging.**

**Heat tint from welding must be removed before passivation.** The dark oxide scale adjacent to a weld is chromium-depleted and is a corrosion initiation site. It is removed by pickling (a stronger acid treatment, typically nitric-hydrofluoric), by mechanical means, or by electropolishing. Passivation alone does not remove it.

---

## Verification

Passivation is invisible. Verification is therefore by test, and several standard tests exist:

| Test | Method | Detects |
|---|---|---|
| **Water immersion** | 24 h in distilled water, inspect for rust | Gross free iron. Simple, cheap, insensitive |
| **High humidity** | 24 h at 97 % RH, 311 K | Free iron. More sensitive than water immersion |
| **Copper sulfate** | Swab with CuSO4 solution, look for copper plating | Free iron. **Sensitive but cannot be used on parts that will see hydrazine or oxygen** because it deposits copper |
| **Potassium ferricyanide-nitric acid** | Swab, look for blue coloration | Free iron. Very sensitive |
| **Salt spray** | ASTM B117, 5 % NaCl fog | General corrosion resistance |
| **XPS / ESCA surface analysis** | Measures the Cr:Fe ratio in the surface film | The actual passive layer quality. Definitive and expensive |

**The copper sulfate test deposits copper.** That is fine for a general part and unacceptable for anything that will contain hydrazine (copper catalyzes decomposition) or oxygen (copper is a contaminant). Specify the test method with the fluid service in mind.

**Cr:Fe ratio** is the fundamental measure. A well-passivated 316L surface has a surface chromium to iron ratio above about 1.0; an electropolished surface can exceed 1.5. An untreated machined surface is around 0.5.

---

## Passivation of other alloys

**Aluminum** does not need passivation in the stainless sense; it forms its own oxide immediately. What aluminum needs is **conversion coating** (chromate per MIL-DTL-5541, or a trivalent chromium or non-chromate alternative) or **anodizing**, both of which thicken and stabilize the natural oxide.

Note that anodized aluminum in a fluid system is a mixed blessing: the anodic layer is hard and corrosion resistant, but it is also porous, it traps contamination, and it can spall. Sealed anodize or bare aluminum are often preferable inside a fluid system.

**Titanium** forms a tenacious oxide and needs no passivation. It does need cleaning, and it must be handled to avoid embedding iron, which causes crevice corrosion.

**Nickel alloys** (Inconel, Monel) can be passivated in nitric acid to remove free iron, using the same reasoning as stainless.

**Copper alloys** should not be in an aerospace fluid system for hydrazine or oxygen service at all.

---

## Propellant passivation: a different meaning

For certain propellants, the system must be **conditioned to the propellant** before it can be used. This is a completely different process from chemical passivation and it is confusingly given the same name.

**Fluorine and fluorine-containing oxidizers.** Fluorine reacts with almost every metal to form a fluoride film. If that reaction happens all at once when the system is loaded, it is violent. The system is therefore passivated by exposing it to progressively increasing concentrations of fluorine, starting very dilute, allowing a protective fluoride film to build up slowly. The passivated film then protects the metal in service. **An unpassivated fluorine system will burn.**

**Nitrogen tetroxide (N2O4).** NTO reacts with residual moisture to form nitric acid, which attacks the system. Passivation consists of drying the system thoroughly and then exposing it to NTO vapor to form a stable surface layer before liquid loading.

**Hydrogen peroxide.** HTP decomposes catalytically on almost any contaminated surface. A peroxide system is passivated by successive rinses of increasing peroxide concentration, each of which decomposes on and consumes the remaining catalytic contamination. The system is considered passivated when the decomposition rate falls below a specified value, measured as gas evolution or as a concentration loss rate. **This is a functional test, not a procedural step**: the system is passivated when it demonstrably stops decomposing the propellant.

**Hydrazine** does not require propellant passivation in the same sense, provided the material selection is correct. What it requires is that no catalytic material be present in the first place; there is no film that can be built up to protect against a copper fitting.

---

## Spacecraft passivation: a third meaning

**Orbital debris mitigation** requires that a spacecraft at end of mission be rendered incapable of generating debris through a stored energy release. That is called passivation and it is a requirement, not a good practice:

| Energy source | Passivation action |
|---|---|
| Residual propellant | Vent or burn to depletion |
| Pressurant | Vent to ambient |
| Pressurized tanks | Vent, and leave vent valves open |
| Batteries | Discharge and disconnect from charging |
| Momentum wheels | Spin down |
| Deployment mechanisms | Safe or fire |

The relevant requirements are **NASA-STD-8719.14**, **ESA ISO 24113**, and the **IADC Space Debris Mitigation Guidelines**. The fluid system consequence is that the design must include a way to vent every pressurized volume at end of life, which means vent valves, their commands, their power, and their inclusion in the reliability analysis. **A design that cannot be passivated cannot be licensed.**

Note the tension with normal fluid system design practice: everything else in this library argues for eliminating leak paths, and this requirement adds one deliberately. It is resolved with a normally closed pyrotechnic or latching valve that is fired once, at end of life, and never needs to reseal.

---

## Design rules of thumb

| Rule | Value | Why |
|---|---|---|
| Passivate after all welding and grinding | Always | Welding destroys the film and adds heat tint |
| Degrease before passivating | Always | Oil shields the surface and the passivation is worthless |
| Remove weld heat tint before passivating | Always | Passivation does not remove scale |
| Default process | Citric acid, ASTM A967 / AMS 2700 Method 2 | No hex chrome, benign waste |
| Ultra-high-purity, vacuum, small bore | Electropolish | Better Cr:Fe ratio and a smoother surface |
| Citric film development time | 24 to 48 h before verification | The film forms in air after the bath |
| Verification test | Not copper sulfate for hydrazine or oxygen hardware | It deposits copper |
| Surface Cr:Fe ratio target | > 1.0 passivated, > 1.5 electropolished | The fundamental measure |
| Sequence | Machine, weld, blend, degrease, passivate, clean, package | Passivation is second to last |
| Internal surfaces of tubing | Circulate the solution or electropolish | An immersion bath does not reach a long bore |
| Fluorine, NTO, HTP systems | Propellant passivation required, separately | A different process with the same name |
| Spacecraft end of life | Vent every pressurized volume | NASA-STD-8719.14 |

---

## Failure modes

**Passivating a greasy part.** The most common failure. The oil shields the surface, the acid does nothing there, and the part comes out with a patchwork of passivated and unpassivated areas that is invisible until it rusts.

**Passivating before the last weld.** The weld destroys the film locally and the part goes into service with an unpassivated, heat-tinted, chromium-depleted weld zone.

**Embedded iron from carbon steel tooling.** A stainless part machined with tooling that has been used on carbon steel, or blasted with media that has been used on carbon steel, picks up iron. If the passivation does not fully remove it, rust blooms in service.

**Over-etching a weld or a fine feature.** Nitric acid at too high a concentration or temperature can attack weld metal preferentially, particularly on free-machining or sensitized material. Feature dimensions change.

**Hydrogen embrittlement of high strength steel.** Acid treatment of a high strength martensitic or precipitation hardened steel can charge hydrogen into the metal. A bake-out after treatment is required for anything above about 1000 MPa ultimate strength.

**Copper sulfate test on hydrazine hardware.** Deposits copper, which then catalyzes propellant decomposition. The verification test contaminates the part it was verifying.

**Passivation solution trapped in a crevice.** A socket weld crevice, a blind hole, or a dead leg holds acid that is never rinsed out. It corrodes from the inside.

**No end-of-life vent path.** Discovered during the debris mitigation review, when the design is frozen.

---

## Operations

**Degrease, then passivate, then clean.** Three separate operations with three separate purposes. Do not conflate them on a drawing.

**Rinse thoroughly, with deionized water**, and verify by conductivity of the final rinse. Residual acid is worse than no passivation.

**Dry completely.** Trapped water in a crevice after passivation is a corrosion cell.

**Handle with clean gloves after passivation.** A fingerprint is a chloride source, and chloride on a freshly passivated stainless surface in a humid environment initiates pitting.

**Package immediately** in a clean, sealed bag with the caps installed. The passive layer is robust but the surface cleanliness is not.

**Document the process, the bath, the temperature, the time and the verification result.** For flight hardware this is a traceability requirement and for everything else it is what lets you diagnose a corrosion problem two years later.

**Re-passivate after any rework** that involves grinding, welding or machining.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM A967** | Chemical passivation treatments for stainless steel parts. The primary reference |
| **AMS 2700** | Passivation of corrosion resistant steels (aerospace). Method 1 nitric, Method 2 citric |
| ASTM A380 | Cleaning, descaling and passivation of stainless steel parts, equipment and systems |
| ASTM B912 | Passivation of stainless steels using electropolishing |
| ASTM A967 Practice C | Copper sulfate test |
| ASTM A967 Practice E | Potassium ferricyanide-nitric acid test |
| QQ-P-35 | Passivation treatments for corrosion resistant steel (superseded by AMS 2700) |
| SAE AMS 2431 | Electropolishing |
| MIL-DTL-5541 | Chemical conversion coatings on aluminum |
| MIL-A-8625 | Anodic coatings for aluminum |
| ASTM G93 | Cleaning methods and cleanliness levels for oxygen service |
| NASA-STD-8719.14 | Process for limiting orbital debris (spacecraft passivation) |
| ISO 24113 | Space systems: space debris mitigation requirements |

---

## References

1. ASTM A967/A967M, *Standard Specification for Chemical Passivation Treatments for Stainless Steel Parts*.
2. SAE AMS 2700, *Passivation of Corrosion Resistant Steels*.
3. ASTM A380/A380M, *Standard Practice for Cleaning, Descaling, and Passivation of Stainless Steel Parts, Equipment, and Systems*.
4. Tuthill, A. H. and Avery, R. E., "Specifying Stainless Steel Surface Treatments", *Nickel Development Institute*, No. 10068.
5. Nickel Institute, *Cleaning and Descaling Stainless Steels*, Publication 9001.
6. Schutz, R. W. and Thomas, D. E., "Corrosion of Titanium and Titanium Alloys", *ASM Handbook Volume 13*.
7. NASA-STD-8719.14C, *Process for Limiting Orbital Debris*.
8. Clark, J. D., *Ignition!*, Rutgers University Press, 1972 (fluorine passivation, in a very direct style).
