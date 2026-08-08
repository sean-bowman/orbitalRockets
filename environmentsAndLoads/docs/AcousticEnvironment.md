[Home](../README.md) > Acoustic Environment

# Acoustic Environment

## Contents

- [Overview](#overview)
- [Decibels do not add arithmetically](#decibels-do-not-add-arithmetically)
- [The two acoustic phases](#the-two-acoustic-phases)
- [Bands](#bands)
- [Vibroacoustic response](#vibroacoustic-response)
- [Acoustic test against shaker test](#acoustic-test-against-shaker-test)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

The acoustic field at liftoff is the source of most of the random vibration a launch vehicle sees. Understanding it is understanding where the vibration environment comes from, which is why this document and [RandomVibration.md](RandomVibration.md) belong together.

---

## Decibels do not add arithmetically

**Sound pressure level is a logarithmic quantity referenced to 20 micropascals:**

```
SPL = 20 log10( p / 20e-6 )
```

**Levels combine by adding power, not by adding decibels:**

```
OASPL = 10 log10( sum of 10^(L_i / 10) )
```

**Two uncorrelated 140 dB sources give exactly 143.01 dB.** Not 280, and not 140. That is the single most common error in acoustic work and it is worth committing to memory: doubling the power is +3 dB, always.

| Combination | Result |
|---|---|
| Two equal sources | +3.01 dB |
| Ten equal sources | +10 dB |
| One source 10 dB below another | +0.41 dB, essentially nothing |

**The last row is why the overall level is dominated by the loudest few bands.** A band 10 dB down contributes almost nothing, so quieting it changes nothing.

---

## The two acoustic phases

| Phase | Source | Character |
|---|---|---|
| **Liftoff** | Engine exhaust, reflected off the pad and flame trench | **Loudest.** Broadband, 5 to 10 s |
| **Transonic** | Aerodynamic, shock oscillation, separated flow | Shorter, higher frequency emphasis |

**Liftoff is usually the louder** and it is heavily influenced by the pad. Exhaust deflectors, flame trench geometry and water suppression all change it, sometimes by 5 to 10 dB, which means a pad change is an environment change.

**Water sound suppression is worth several decibels** and it is one of the few environment reductions available to a programme after the vehicle is designed.

**Transonic often governs a particular component** even when liftoff is louder overall, because its energy sits higher in frequency where small hardware resonates.

---

## Bands

**Acoustic specifications are written in octave or one-third octave bands**, not as a continuous spectrum.

| Band type | Resolution | Use |
|---|---|---|
| **Octave** | 9 bands, 31.5 Hz to 8 kHz | Specification, reporting |
| **One-third octave** | 26 bands | Analysis, test control |

**Band level is not spectral density.** A wider band contains more energy at the same density, so comparing a level across band types without converting is meaningless. One-third octave levels are about 4.8 dB below the octave band containing them, for a flat spectrum.

---

## Vibroacoustic response

**The panel is what converts sound into vibration.** A large lightweight panel immersed in an acoustic field responds, and that response is the random vibration environment for everything mounted to it.

**The dominant scaling is surface mass:**

```
response ~ p^2 / m^2
```

**Response goes as the inverse square of surface mass.** Doubling the areal mass quarters the acceleration response, which is why lightweight structure is the vibroacoustic problem and dense structure is not.

**Adding mass to reduce vibroacoustic response works and it is usually the wrong trade**, because the mass costs more than the qualification does.

**Coincidence is the other effect.** At the frequency where the acoustic wavelength matches the panel's bending wavelength, the coupling becomes very efficient and the response peaks. Below coincidence the panel is an inefficient radiator and receiver; above it, efficient.

**The estimate is a correlation, good to a factor of two or three.** That is enough to decide whether a zone is acoustically driven or structure-borne, and not enough to set a test level.

---

## Acoustic test against shaker test

**They load the article differently and the right choice follows from what the article is.**

| | Acoustic chamber | Shaker |
|---|---|---|
| **Load path** | **Over the whole surface**, as in flight | Through the mounting feet |
| **Best for** | **Large light structure**, panels, solar arrays, fairings | Small dense units |
| **Frequency range** | Wide, limited at the low end by chamber size | Wide, limited at the high end |
| Cost | Higher facility cost | Lower |
| Fixturing | Minimal | A designed fixture, itself a problem |

**For a large light panel the shaker is the wrong load path.** Flight loads it as a pressure over its area; a shaker loads it as a base motion at its attachments, and the resulting mode participation is different.

**For a small dense box the acoustic field cannot get enough energy in.** Its surface area is small and its mass is large, so the response is negligible and a shaker is the only way to reach the environment.

**The crossover is around 10 kg/m^2 of surface mass** and it is not sharp. Many programmes do both: acoustic for the structure, random vibration for the units mounted to it.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Reference pressure | 20 micropascals |
| Two equal sources | +3.01 dB |
| A source 10 dB down | +0.41 dB, negligible |
| Liftoff is usually louder, transonic often governs | Higher frequency |
| Water suppression | Worth several dB |
| Response goes as `1/m^2` | Light panels are the problem |
| One-third octave is ~4.8 dB below its octave | For a flat spectrum |
| Acoustic below ~10 kg/m^2, shaker above | Not a sharp line |

---

## Failure modes

**Decibels added arithmetically.** Wrong by tens of decibels.

**Band levels compared across octave and one-third octave.** Different bandwidths.

**A shaker used on a large light panel.** Wrong load path, wrong mode participation.

**An acoustic test used on a dense box.** Not enough energy coupled in.

**A pad change treated as not affecting the environment.** It can be 5 to 10 dB.

**Vibroacoustic estimate used to set a test level.** It is good to a factor of two.

**Mass added to fix a vibroacoustic problem.** It works and it usually costs more than qualifying.

---

## Worked numbers

From [`AcousticSpec`](../environmentsAndLoadsLibrary/AcousticSpec.py):

| Environment | OASPL |
|---|---|
| Small launcher fairing | 138.9 dB |
| Medium launcher fairing | 142.4 dB |
| **Engine compartment** | **154.3 dB** |

For the medium launcher fairing, the overall level is **5.4 dB above its loudest single band**, and the 250 Hz band carries 29 percent of the total power.

| Surface mass | Estimated response |
|---|---|
| 2.0 kg/m^2 | 4x the 8 kg/m^2 case |
| 8.0 kg/m^2 | reference |

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-7001** | Payload vibroacoustic test criteria |
| NASA-HDBK-7005 | Dynamic environmental criteria |
| MIL-STD-1540 | Test requirements |
| MIL-STD-810 Method 515 | Acoustic noise test methods |
| ISO 266 | Preferred frequencies for acoustic measurements |
| ANSI S1.11 | Octave band and fractional octave band filters |

---

## Tool interface

```python
import sys
sys.path.insert(0, 'environmentsAndLoadsLibrary')

from AcousticSpec import AcousticSpec, REFERENCE_ENVIRONMENTS

# the canonical decibel addition check
pair = AcousticSpec()
pair.setInputs({'bandCentres': [125.0, 250.0], 'bandLevels': [140.0, 140.0]})
print(f'two 140 dB sources -> {pair.calculateOverallLevel()["overallLevel"]:.2f} dB')

for name in REFERENCE_ENVIRONMENTS:
    acoustic = AcousticSpec()
    acoustic.setInputs({'referenceEnvironment': name, 'surfaceMass': 6.5})
    result = acoustic.calculateOverallLevel()
    print(f'{name:26s} {result["overallLevel"]:6.1f} dB OASPL')
```

---

## References

1. NASA-STD-7001B, *Payload Vibroacoustic Test Criteria*.
2. Barrett, R. E., *Techniques for Predicting Localized Vibratory Environments of Rocket Vehicles*, NASA TN D-1836, 1963.
3. Eldred, K. M., *Acoustic Loads Generated by the Propulsion System*, NASA SP-8072, 1971.
