[Home](../README.md) > Alloys

# Alloys for LPBF

## Contents

- [Overview](#overview)
- [What makes an alloy printable](#what-makes-an-alloy-printable)
- [The mature alloys](#the-mature-alloys)
- [Why copper is hard](#why-copper-is-hard)
- [Why aluminium is hard for different reasons](#why-aluminium-is-hard-for-different-reasons)
- [Cracking-limited alloys](#cracking-limited-alloys)
- [Alloys designed for the process](#alloys-designed-for-the-process)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The set of alloys that print well is small, and it is not the set anyone would have chosen. It is the set whose properties happen to suit a process that melts 40 micrometres at a time and cools at a million kelvin per second.

Several excellent structural alloys cannot be printed at all, and several mediocre ones print beautifully.

---

## What makes an alloy printable

Four properties, and an alloy needs all four.

**Absorptivity at 1070 nm.** The fraction of incident laser energy that enters the melt pool. Below about 0.2 the process becomes marginal at any power, and this is the one that eliminates copper.

**Moderate thermal diffusivity.** Too low and the heat cannot escape, so the pool grows uncontrollably. Too high and it escapes before it can melt anything, which is aluminium's problem.

**A narrow freezing range.** A wide range means a long mushy zone behind the pool, which is where solidification cracking happens.

**No brittle phase on rapid cooling.** Some alloys form intermetallics or martensite at 1e6 K/s that they never form conventionally.

| Alloy | Absorptivity | Diffusivity [m^2/s] | Verdict |
|---|---|---|---|
| 316L | 0.38 | 5.0e-6 | The easiest. Develop parameters on it |
| Inconel 718 | 0.42 | 5.5e-6 | Mature |
| Inconel 625 | 0.42 | 5.2e-6 | Mature |
| Ti-6Al-4V | 0.40 | 8.0e-6 | Mature, and reactive |
| AlSi10Mg | 0.25 | 5.0e-5 | Harder. High power, fast scanning |
| **GRCop-42** | **0.15** | **9.4e-5** | **Hard on both counts** |

---

## The mature alloys

| Alloy | Why it is used | What it needs |
|---|---|---|
| **316L** | The learning alloy. Very forgiving, wide process window, no cracking | Nothing special. Stress relief optional for most geometry |
| **Inconel 718** | The workhorse. Strength from 20 K to 925 K in one alloy | HIP for fatigue, then solution and age. The HIP runs above the gamma prime solvus so a re-treat is mandatory |
| **Inconel 625** | Solid solution, so no post-build age is needed to reach properties | Stress relief. Nothing else |
| **Ti-6Al-4V** | The best strength to weight, and a wide process window | Inert handling; the powder is reactive. Stress relief on the plate is mandatory or it distorts badly |
| **AlSi10Mg** | The default additive aluminium | High power and fast scanning. Moisture control on the powder |
| **17-4PH** | Where a hard, machinable stainless is needed | Solution and age. The as-built structure is heavily retained austenite |

**316L is where a programme should start.** Its window is wide enough that a mediocre parameter set still produces a dense part, so the machine, the powder handling and the process discipline can be shaken out without the alloy fighting back.

---

## Why copper is hard

**Copper reflects the fibre laser wavelength.** Pure copper absorbs about 5 percent at 1070 nm, so 95 percent of the beam bounces off. What does enter is then conducted away almost instantly, because copper's thermal diffusivity is the highest of any engineering metal.

Both problems point the same way and they compound.

**GRCop-42 works because it was designed to.** Chromium and niobium raise the absorptivity to about 0.15, which is still poor and is enough for a conventional machine. The Cr2Nb dispersoids that give it elevated temperature strength are a second reason for the alloy, and the two purposes are why it exists in the form it does rather than as a simpler copper alloy.

**The numbers, from [`LpbfProcess`](../additiveLpbfLibrary/LpbfProcess.py):**

| Alloy | Power | E_v [J/mm^3] | dH/h_s | Regime |
|---|---|---|---|---|
| Inconel 718 | 285 W | 67.5 | 13.5 | stable |
| GRCop-42 | 300 W | 85.2 | 2.2 | lack of fusion |
| GRCop-42 | 500 W | 162.3 | 4.0 | lack of fusion |

**GRCop-42 at 500 W has more than twice the energy density of the stable nickel set and it is still lack of fusion.** That is the absorptivity, and it is why copper parts need machines built for them rather than a parameter change.

**Green and blue lasers change the picture.** Copper absorbs 40 to 60 percent at 515 nm against 5 percent at 1070. Machines with green sources are becoming available and they make pure copper printable. As of now, GRCop-42 on a standard infrared machine is the mature route.

---

## Why aluminium is hard for different reasons

Aluminium's absorptivity is poor but not catastrophic. Its problems are elsewhere.

**Thermal diffusivity of 5e-5 m^2/s**, ten times nickel. Heat leaves the pool almost as fast as it arrives, so a slow scan simply heats the whole part rather than melting a pool. Aluminium needs high power AND fast scanning, and the two together demand a machine with the power and the scanner speed to deliver it.

**A tenacious oxide.** Aluminium oxide melts at 2345 K against 869 K for the alloy, so it does not melt in the pool. It gets stirred in as film fragments and it interferes with wetting between tracks.

**Hydrogen porosity.** Aluminium dissolves hydrogen readily when molten and rejects it on freezing. The hydrogen comes from moisture on the powder, so powder that has been open to humid air produces porosity that no parameter change fixes. **Aluminium powder handling is a moisture control problem more than anything else.**

**Low as-built strength relative to wrought.** AlSi10Mg is a casting alloy and it reaches around 250 MPa yield as built. There is no additive equivalent of 7075 in production, because the high strength 7xxx alloys crack during solidification.

---

## Cracking-limited alloys

Some alloys cannot be printed because they crack while solidifying, and the mechanism is worth understanding because it explains the pattern.

**Solidification cracking.** The last liquid to freeze sits in thin films between dendrites. The surrounding solid contracts, pulls those films apart, and there is not enough liquid left to feed the gap. A wide freezing range gives a long mushy zone and more opportunity for it.

**Strain age cracking.** In precipitation hardened nickel alloys, gamma prime precipitates during cooling in the heat affected zone, which is simultaneously under high residual stress. The alloy hardens and is strained at the same time, and it cracks.

| Alloy | Status | Why |
|---|---|---|
| **7075, 2024 aluminium** | Not printable conventionally | Wide freezing range, severe solidification cracking |
| **Inconel 738, Rene 41** | Very difficult | High gamma prime, strain age cracking |
| **Inconel 718** | Printable | Low enough gamma prime, and it forms slowly |
| Tool steels | Printable with preheat | Martensite formation; a heated plate is required |

**The 7075 problem has been solved in the laboratory** by adding nucleating particles, typically zirconium hydride, to refine the grain structure so the mushy zone can feed. It is not a production process as of now.

---

## Alloys designed for the process

The interesting development is alloys designed for additive rather than adapted to it.

| Alloy | Designed for |
|---|---|
| **GRCop-42** | Additive from the start. Absorptivity and thermally stable dispersoids |
| Scalmalloy | High strength additive aluminium. Scandium refines the grain and prevents cracking |
| **NASA HR-1** | Hydrogen resistant additive superalloy, for hydrogen turbomachinery |
| Ti-6Al-4V ELI, additive grade | Tightened interstitials, because the process adds oxygen |

**This is where the field is going.** An alloy that was optimised for casting or forging is being asked to do something neither process does, and designing for the actual solidification conditions produces better results than adaptation.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Start a programme on 316L | Widest window, most forgiving |
| Absorptivity below 0.2 | Marginal at any power |
| Copper on an infrared machine | GRCop-42 only, and it needs high power |
| Aluminium | High power AND fast scanning, plus moisture control |
| 7xxx and 2xxx aluminium | Not printable in production |
| High gamma prime nickel | Strain age cracking; avoid or preheat |
| 718 HIP | Above the solvus, so a re-treat is mandatory |
| Titanium | Inert handling, and stress relief on the plate |

---

## Failure modes

**Copper attempted on a standard machine at nickel parameters.** Lack of fusion at any energy density.

**Aluminium printed from powder that has been open to humid air.** Hydrogen porosity throughout.

**7075 attempted.** Solidification cracking.

**A high gamma prime superalloy attempted without preheat.** Strain age cracking in the HAZ.

**718 HIPed and not re-solutioned.** Soft, and outside every allowable.

**A wrought alloy's allowables applied to its additive namesake.** They are different materials.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM F3055** | Additive Inconel 718 |
| ASTM F3056 | Additive Inconel 625 |
| ASTM F3184 | Additive 316L |
| **AMS 4999** | Additive Ti-6Al-4V |
| ASTM F3318 | Additive AlSi10Mg |
| ASTM F3301 | Post-processing methods for metal additive parts |
| NASA-STD-6030 | Additive manufacturing requirements |

---

## Tool interface

```python
from LpbfProcess import LpbfProcess, MELT_PROPERTIES

# The absorptivity that decides whether an alloy is printable at all
for alloy, entry in sorted(MELT_PROPERTIES.items(),
                           key = lambda item: item[1]['absorptivity']):
    print(f'{alloy:14s} A = {entry["absorptivity"]:.2f}  '
          f'alpha = {entry["thermalDiffusivity"]:.1e}')

# And the consequence
process = LpbfProcess()
process.setInputs({'material': 'GRCop-42', 'laserPower': 500.0, 'scanSpeed': 0.70})
process.calculateEnergyDensity()
print(process.classifyRegime()['processRegime'])     # still lack of fusion
```

---

## References

1. Ellis, D. L., *GRCop-84: A High Temperature Copper Alloy for High Heat Flux Applications*, NASA/TM-2005-213566.
2. Gradl, P. R. et al., "GRCop-42 Development and Hot-fire Testing", AIAA Propulsion and Energy, 2019.
3. Martin, J. H. et al., "3D Printing of High-Strength Aluminium Alloys", *Nature*, Vol. 549, 2017.
4. Aboulkhair, N. T. et al., "3D Printing of Aluminium Alloys", *Progress in Materials Science*, Vol. 106, 2019.
5. Sanchez, S. et al., "Powder Bed Fusion of Nickel-Based Superalloys: A Review", *International Journal of Machine Tools and Manufacture*, Vol. 165, 2021.
