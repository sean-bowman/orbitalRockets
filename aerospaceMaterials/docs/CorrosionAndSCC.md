[Home](../README.md) > Corrosion and SCC

# Corrosion and Stress Corrosion Cracking

## Contents

- [Overview](#overview)
- [Galvanic corrosion, quantified](#galvanic-corrosion-quantified)
- [The area ratio rule](#the-area-ratio-rule)
- [Pitting resistance](#pitting-resistance)
- [Crevice corrosion](#crevice-corrosion)
- [Stress corrosion cracking](#stress-corrosion-cracking)
- [The short transverse problem](#the-short-transverse-problem)
- [Protection, in order of effectiveness](#protection-in-order-of-effectiveness)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The galvanic series and the compatibility matrices are in [fluidSystems MaterialsCompatibility.md](../../fluidSystems/fluidSystemsLibrary/docs/MaterialsCompatibility.md) and are not repeated here. This document covers the mechanisms and the quantification: how fast, how deep after ten years, at what stress, and what actually to do about it.

The distinction matters because a compatibility table answers whether a combination is permitted, and a design review asks how much margin there is.

---

## Galvanic corrosion, quantified

Two dissimilar metals in electrical contact with an electrolyte form a cell. The more anodic one dissolves.

**The driving potential** is the difference in anodic index per MIL-STD-889B:

| Environment | Permitted difference |
|---|---|
| Controlled indoor | 0.50 V |
| Normal, sheltered | 0.25 V |
| **Launch site marine** | **0.15 V** |
| Harsh, immersion, splash zone | 0.15 V |

**A coastal launch site is a marine environment** and it takes the tightest limit. That single fact rules out most dissimilar metal joints unless they are isolated.

**The rate** follows from Faraday's law once a current density is estimated:

```
rate [m/s] = i_anode * equivalentWeight / (F * rho)
```

**Read the absolute rate as an order of magnitude, not a prediction.** The couple current density is a crude stand-in for a real polarisation curve, and on a passive alloy like titanium it overstates the rate by orders of magnitude because the passive film is not modelled. What the calculation is genuinely good for is comparing two candidate joints and getting the direction of the area ratio effect right.

---

## The area ratio rule

**This is the rule people get backwards, and getting it backwards makes things worse.**

The couple current is set by the cathode area and it all flows out of the anode. Concentrating that current onto a small anode gives a high local current density and rapid penetration.

| Configuration | Outcome |
|---|---|
| **Small anode, large cathode** | **Catastrophic.** All the current on a small area |
| Large anode, small cathode | Benign. The current is spread thin |

**A steel fastener in an aluminium plate is fine.** The aluminium anode is enormous relative to the steel cathode, so the penetration is spread over a large area and is negligible.

**An aluminium fastener in a steel plate is destroyed.** The same couple, the ratio inverted, and the entire current concentrated on the fastener.

**The same logic governs coatings**, and it is why the coat-the-cathode rule exists. A coating always has holidays. **Coating only the anode concentrates the whole couple current onto those holidays and produces faster local penetration than no coating at all.** Coat the cathode; coat both if either is coated. The [`CorrosionAssessment`](../aerospaceMaterialsLibrary/CorrosionAssessment.py) class states this explicitly in its recommendations rather than leaving it to the reader.

---

## Pitting resistance

```
PREN = %Cr + 3.3 (%Mo + 0.5 %W) + 16 %N
CPT [degC] = 2.5 PREN - 71
```

Above the critical pitting temperature, chlorides initiate stable pits. Below it they do not.

| Alloy | PREN | CPT | Pits at ambient? |
|---|---|---|---|
| 321 / 347 | 18.0 | -26 degC | **Yes** |
| 304L | 19.3 | -23 degC | **Yes** |
| **316L** | **26.1** | **-6 degC** | **Yes** |
| A286 | 19.4 | -22 degC | Yes |
| Inconel 718 | 29.1 | +2 degC | Marginal |
| **Inconel 625** | **51.2** | **+57 degC** | No |
| Hastelloy X | 52.7 | +61 degC | No |

**316L pits at ambient temperature in chlorides.** That is the single most useful corrosion number in this document, and it explains why launch site hardware corrodes in ways that laboratory hardware does not.

**Pitting is dangerous out of proportion to the metal lost.** A pit is a stress concentration and a crack initiation site, and it penetrates while the surrounding surface stays bright. The mass loss is trivial and the structural consequence is not.

**Passivation per AMS 2700 restores the chromium oxide film** and removes free iron from the surface. It does not raise the critical pitting temperature. Only alloy content does.

---

## Crevice corrosion

The same mechanism as pitting, initiated by geometry rather than by a surface defect. Inside a crevice the electrolyte becomes oxygen depleted and chloride enriched, the local pH falls, and the passive film breaks down.

**Crevice corrosion initiates at a lower temperature than pitting** on the same alloy, typically 10 to 20 degrees lower, because the geometry does the work the surface defect would otherwise have to do.

| Crevice source | Control |
|---|---|
| Flange faces and gaskets | Full face gaskets, avoid partial contact |
| Under fastener heads and washers | Wet install with sealant |
| Lap joints | Seal, or design as a butt joint |
| Under deposits and scale | Cleanliness and drainage |
| Under tape and labels | Remove before service |

**Design to drain.** A geometry that traps water at a launch site will corrode, and no material selection fixes a design that holds a puddle.

---

## Stress corrosion cracking

Three things simultaneously: a susceptible material, a specific environment, and a sustained tensile stress. Remove any one and it does not happen.

**It is specific pairs, not a general tendency.** A material immune in one environment cracks in another.

| Material | Environment | Threshold |
|---|---|---|
| **7075-T6, short transverse** | Marine air | **50 MPa** |
| 7075-T73, short transverse | Marine air | 240 MPa |
| 300 series stainless | Hot chlorides | 40 to 55 MPa |
| **Titanium** | **Methanol** | **8 MPa** |
| Titanium | Uninhibited N2O4 | 12 MPa |
| High strength steel | Hydrogen, H2S | 40 to 170 MPa |
| 17-4PH H900 | Marine air | 200 MPa |

**The fracture mechanics form** is more useful than the threshold stress for a part with a known flaw:

```
K_applied = Y sigma sqrt(pi a)
```

If `K_applied` exceeds `K_ISCC`, the crack grows at the stage II plateau velocity, which is independent of `K`. The time to failure follows directly from the distance the crack has to travel:

```
t_failure = (a_critical - a_initial) / v_plateau
```

**Sustained stress is what matters, not cyclic.** Residual stress from machining, forming or an interference fit counts, and it is the source people forget because it does not appear in a load case.

---

## The short transverse problem

**Short transverse is the through-thickness direction of a rolled or forged product**, and it is where SCC lives.

Rolling and forging elongate the grains along the working direction. A stress in the short transverse direction presents itself broadside to the grain boundaries, which is the crack path, and it also encounters the highest density of them.

| Direction | Relative SCC threshold in 7xxx |
|---|---|
| Longitudinal | 1.0 |
| Long transverse | 0.6 |
| **Short transverse** | **0.15** |

**A designer who quotes a longitudinal allowable for a short transverse load has overstated the SCC threshold by nearly seven times.**

**Where short transverse tension arises without anyone intending it:**

- A bolt torqued through a thick plate, clamping across the thickness
- An interference fit pin in a thick lug
- Residual stress from machining a thick quenched plate asymmetrically
- A shrink fit
- A part machined from plate where the load turns out to run through the thickness

**The fix is the temper.** T73 or T7451 rather than T6, at a cost of about 13 percent of the yield strength.

---

## Protection, in order of effectiveness

| Measure | Why it is ranked here |
|---|---|
| **1. Eliminate the couple** | The only fix that cannot degrade in service |
| **2. Electrically isolate** | Must interrupt every metallic path including fasteners, and be verified by resistance measurement |
| **3. Coat the cathode** | And coat the anode too if either is coated. Never the anode alone |
| **4. Reverse the area ratio** | Make the anode the large member. The rate scales directly |
| **5. Seal the joint** | Wet-installed sealant so there is no continuous electrolyte path |
| **6. Sacrificial anode** | Adds a third, more anodic material to be consumed |
| **7. Accept with inspection** | Interval computed from the penetration rate, with the allowance recorded |

**Isolation has to be verified, not inspected.** A resistance measurement across the joint is the check; a visual inspection of a sleeve tells you nothing about whether a fastener is bridging it.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Launch site potential limit | 0.15 V |
| Small anode, large cathode is catastrophic | The rate scales with the ratio |
| Coat the cathode, never only the anode | Otherwise it is worse than no coating |
| PREN 26 means it pits at ambient | Passivation does not change that |
| Crevice initiates 10 to 20 K below pitting | Design to drain |
| T73 not T6 for any sustained ST stress | 50 MPa versus 240 MPa |
| Short transverse threshold is 15 % of longitudinal | And it is the direction least often checked |
| Residual stress counts as sustained stress | It is not in any load case |
| Verify isolation by resistance | Not by inspection |

---

## Failure modes

**An aluminium part destroyed next to a small stainless one.** Inverted area ratio.

**A coating on the anode only.** All the current on the holidays, faster than no coating.

**316L pitting at a coastal site.** Its critical pitting temperature is below ambient.

**A 7075-T6 fitting cracking in storage.** Short transverse residual stress and humid air. No load required.

**Titanium cracked by a cleaning solvent.** Methanol at 8 MPa.

**Crevice corrosion under a gasket.** Nothing visible until the flange leaks.

**Isolation defeated by a fastener.** The sleeve was installed and the bolt bridged it.

**A design that traps water.** No material selection fixes a puddle.

---

## Standards

| Standard | Scope |
|---|---|
| **MIL-STD-889** | Dissimilar metals, the anodic index source |
| **ASTM G82** | Development and use of a galvanic series |
| ASTM G71 | Conducting and evaluating galvanic corrosion tests |
| **ASTM G48** | Pitting and crevice corrosion resistance by ferric chloride |
| ASTM G150 | Critical pitting temperature |
| **ASTM G47** | SCC susceptibility of 2xxx and 7xxx aluminium |
| ASTM G30 / G39 | U-bend and bent-beam stress corrosion specimens |
| ASTM G49 | Direct tension stress corrosion test specimens |
| **AMS 2700** | Passivation of corrosion resistant steels |
| ASTM A380 | Cleaning, descaling and passivation of stainless |
| NASA-STD-6016 | Materials and processes, including SCC table requirements |
| **MSFC-SPEC-522** | Design criteria for controlling stress corrosion cracking |

---

## Tool interface

```python
from CorrosionAssessment import CorrosionAssessment

corrosion = CorrosionAssessment()
corrosion.setInputs({'anodeMaterial': '6061', 'anodeCondition': 't6',
                     'cathodeMaterial': 'Ti-6Al-4V', 'cathodeCondition': 'annealed',
                     'anodeArea': 0.008, 'cathodeArea': 0.0012,
                     'environment': 'launch site marine',
                     'serviceLife': 10.0 * 3.156e7,
                     'corrosionAllowance': 0.0002,
                     'appliedStress': 120.0e6, 'orientation': 'ST'})

corrosion.calculateGalvanicCouple()       # potential, area ratio, penetration over life
corrosion.calculatePittingResistance()    # PREN and critical pitting temperature
corrosion.assessStressCorrosion()         # raises on ST tension in a susceptible alloy
corrosion.recommendProtection()           # ordered, with coat-the-cathode enforced
print(corrosion.generateReport())
```

---

## References

1. Jones, D. A., *Principles and Prevention of Corrosion*, 2nd ed., Prentice Hall, 1996.
2. MIL-STD-889C, *Dissimilar Metals*.
3. Sedriks, A. J., *Corrosion of Stainless Steels*, 2nd ed., Wiley, 1996.
4. MSFC-SPEC-522B, *Design Criteria for Controlling Stress Corrosion Cracking*.
5. Speidel, M. O., "Stress Corrosion Cracking of Aluminum Alloys", *Metallurgical Transactions A*, Vol. 6, 1975.
