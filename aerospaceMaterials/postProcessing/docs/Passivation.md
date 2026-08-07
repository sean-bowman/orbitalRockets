[Home](../README.md) > Passivation

# Passivation

## Contents

- [Overview](#overview)
- [What passivation actually does](#what-passivation-actually-does)
- [What it does not do](#what-it-does-not-do)
- [The processes](#the-processes)
- [Verification](#verification)
- [Where it sits in the sequence](#where-it-sits-in-the-sequence)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

Passivation removes free iron from a stainless surface and lets the chromium oxide film reform clean and continuous.

It is widely specified and widely misunderstood, and the misunderstanding is consistent: it is believed to improve the alloy's corrosion resistance, and it does not. It restores what the alloy already had.

**The propellant-side treatment is in [fluidSystems Passivation.md](../../../fluidSystems/fluidSystemsLibrary/docs/Passivation.md)**, which covers passivating a system with its service fluid. This document is the surface treatment.

---

## What passivation actually does

Stainless is corrosion resistant because of a chromium oxide film a few nanometres thick that forms spontaneously in air.

**Manufacturing contaminates that film.**

| Source | Contamination |
|---|---|
| **Machining** | Free iron from tool steel smeared into the surface |
| **Grinding and blasting** | Embedded iron from the media |
| **Forming against carbon steel tooling** | Iron pickup |
| Handling | Iron from fixtures, tables, hands |
| Heat treatment | Scale and a chromium depleted layer |

**Free iron on a stainless surface rusts.** It rusts as iron does, and the rust spot looks like a failure of the stainless when it is contamination sitting on top of it.

**Passivation dissolves the free iron and leaves the chromium behind**, because the acid attacks iron preferentially. The chromium oxide film then reforms over a clean surface.

---

## What it does not do

| Belief | Reality |
|---|---|
| **Improves corrosion resistance** | **No.** It restores what the alloy already had |
| **Raises the pitting resistance** | **No.** PREN is set by alloy content only |
| Adds a coating | No. The film is a few nanometres and it forms itself |
| Fixes sensitization | No. That needs a solution anneal |
| Removes scale | No. Scale needs descaling or pickling first |

**The PREN point is the important one.** A passivated 316L surface has exactly the same critical pitting temperature as an unpassivated one, roughly minus 6 degC, so it still pits at ambient in chlorides. Only a higher alloy content changes that. See [aerospaceMaterials CorrosionAndSCC](../../docs/CorrosionAndSCC.md).

**Passivation is a cleaning operation with a chemical name.**

---

## The processes

| Process | Notes |
|---|---|
| **Nitric acid** | The traditional method. Effective and it is a hazardous waste stream |
| **Citric acid** | Increasingly the default. Less hazardous, comparable results, slower |
| Electropolishing | Passivates as a side effect, and it also removes stock |
| Nitric with dichromate | For free machining grades that nitric alone attacks |

**Citric acid has largely displaced nitric** for environmental and handling reasons, and the standards now treat them as alternatives rather than nitric as the default.

**The free machining grades are the exception.** 303 and similar contain sulphur, and nitric acid attacks the sulphide inclusions and can make the surface worse. Those grades need a specific treatment, and they are best avoided in a corrosion-critical application entirely.

---

## Verification

| Method | What it finds |
|---|---|
| **Water immersion** | Free iron, by rust after 24 hours |
| **High humidity** | Same, faster |
| **Ferroxyl test** | Free iron, chemically. Sensitive, and it contaminates the part |
| **Copper sulphate test** | Free iron, by copper deposition |
| Salt spray | General corrosion performance rather than free iron specifically |

**The copper sulphate test is prohibited on anything that will see hydrazine**, because it deposits metallic copper on the surface and copper catalyses hydrazine decomposition. That is a specific, easily missed prohibition and it appears in the fluidSystems compatibility document for exactly that reason.

**The ferroxyl test contaminates the part** with the reagent, so it is used on samples rather than on flight hardware.

---

## Where it sits in the sequence

| Before | After |
|---|---|
| Final cleaning | All machining |
| Assembly | All grinding and blasting |
| Any cleanliness verification | Heat treatment and descaling |
| | Any handling with iron tooling |

**Passivation is late in the sequence**, after everything that could contaminate the surface and before anything that requires the surface to be clean.

**A part passivated and then machined has an unpassivated machined surface**, and that is a sequencing error that produces rust spots exactly where the machining was.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| It removes free iron | It does not improve the alloy |
| PREN is unchanged | Passivation does not raise the pitting threshold |
| Citric is displacing nitric | Comparable results, less hazardous |
| Free machining grades need a specific process | Or avoid them |
| Late in the sequence | After machining, before assembly |
| **No copper sulphate test near hydrazine** | Copper catalyses decomposition |
| Descale before passivating | It does not remove scale |

---

## Failure modes

**Expected to improve corrosion resistance.** It restores, it does not improve.

**Machined after passivation.** The machined surface is not passivated.

**Copper sulphate test on hydrazine hardware.** Copper deposited on the wetted surface.

**Nitric on a free machining grade.** The surface is worse.

**Scale not removed first.** Passivation does nothing to it.

**Ferroxyl test on flight hardware.** Reagent contamination.

---

## Standards

| Standard | Scope |
|---|---|
| **AMS 2700** | Passivation of corrosion resistant steels |
| **ASTM A967** | Chemical passivation treatments for stainless steel parts |
| ASTM A380 | Cleaning, descaling and passivation of stainless steel |
| ASTM B912 | Passivation by electropolishing |
| QQ-P-35 | Passivation treatments, superseded by AMS 2700 |

---

## References

1. SAE AMS 2700, *Passivation of Corrosion Resistant Steels*.
2. ASTM A967, *Standard Specification for Chemical Passivation Treatments for Stainless Steel Parts*.
3. Sedriks, A. J., *Corrosion of Stainless Steels*, 2nd ed., Wiley, 1996.
