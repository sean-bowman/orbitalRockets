[Home](../README.md) > Chatter and Stability

# Chatter and Stability

## Contents

- [Overview](#overview)
- [Regenerative chatter](#regenerative-chatter)
- [The stability limit](#the-stability-limit)
- [Stability lobes](#stability-lobes)
- [Using the lobe diagram](#using-the-lobe-diagram)
- [Measuring the transfer function](#measuring-the-transfer-function)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Chatter is a self-excited vibration of the machining system that limits the depth of cut. It is a dynamics problem, not a feeds and speeds problem, and treating it as the latter is why so much aerospace machining runs far below its capability.

The important and counter-intuitive result is that at the right spindle speeds the stable depth of cut is several times the average, and finding those speeds is free.

---

## Regenerative chatter

**The mechanism is feedback through the surface the previous tooth left.**

| Step | Detail |
|---|---|
| 1 | A disturbance deflects the tool, leaving a wavy surface |
| 2 | The next tooth cuts that wavy surface, so its chip thickness varies |
| 3 | Varying chip thickness means varying force |
| 4 | Varying force excites the structure further |
| 5 | If the phase is unfavourable, the amplitude grows |

**The phase between the current wave and the previous one is what decides stability**, and that phase depends on the ratio of the tooth passing frequency to the structural natural frequency.

**That is why stability depends on spindle speed in a non-monotonic way.** At some speeds the waves line up in phase and the chip thickness barely varies, so the cut is very stable; at others they are out of phase and it is very unstable.

**Chatter is loud, it leaves a distinctive surface, and it destroys tools.** The surface carries a chatter mark pattern at the chatter frequency rather than the tooth passing frequency, which is how it is identified after the fact.

---

## The stability limit

The critical axial depth of cut is

```
a_lim = -1 / (2 * K_s * Re[G(omega)])
```

| Symbol | Meaning |
|---|---|
| `K_s` | Specific cutting energy |
| `G(omega)` | The tool point frequency response function |
| `Re[G]` | Its real part, which is negative near resonance |

**Only the negative real part matters.** Where `Re[G]` is positive the cut is unconditionally stable at any depth, and the limit comes from the most negative value of the real part.

**The unconditional stability limit** is the depth below which no chatter occurs at any speed:

```
a_min = -1 / (2 * K_s * Re[G]_min)
```

**Three ways to raise it, and they are the only three:**

| Change | Effect |
|---|---|
| **More stiffness** | `Re[G]` scales as `1/k` |
| **More damping** | The peak of `Re[G]` is smaller |
| **A softer material** | `K_s` is smaller |

**Stiffness is usually the accessible one.** A shorter tool overhang is the single most effective change available at the machine, because tool stiffness goes as the inverse cube of the overhang. Halving the overhang multiplies the stiffness by eight and the stability limit with it.

---

## Stability lobes

**Plotting the stability limit against spindle speed produces a scalloped boundary, and the scallops are the useful part.**

Chatter is possible only where the phase is unfavourable. At speeds where the tooth passing frequency is an exact submultiple of the chatter frequency, successive waves are in phase, the chip thickness does not vary, and the cut is stable to a much greater depth.

**The lobe peaks occur at**

```
n = 60 * f_c / (N * k)        k = 1, 2, 3, ...
```

where `f_c` is the chatter frequency in Hz and `N` is the tooth count.

| Lobe number k | Spindle speed | Peak stable depth |
|---|---|---|
| **1** | Highest | **Highest and widest** |
| 2 | Half of lobe 1 | Lower, narrower |
| 3 | A third | Lower still |
| >4 | Low speeds | The lobes merge into the unconditional limit |

**The first lobe is the prize.** It sits at the highest speed and it is the widest, so it is both the most productive and the most tolerant of speed error.

**At high lobe numbers the lobes overlap and disappear** into the unconditional stability limit, which is why low speed machining gets no benefit from speed selection and high speed machining gets a great deal.

**A factor of three to five in stable depth of cut** between an arbitrary speed and a lobe peak is typical, and that is the whole argument for doing the analysis.

---

## Using the lobe diagram

| Step | Detail |
|---|---|
| **1. Measure the FRF** | Tap test at the tool tip, with the actual tool in the actual holder |
| **2. Compute the lobes** | For the material's `K_s` and the tool's flute count |
| **3. Pick a lobe peak** | Prefer the first lobe if the spindle reaches it |
| **4. Set the depth** | Below the peak, with margin for the FRF varying |
| 5. Verify | Sound, surface, and a spindle power trace |

**Stay inside the lobe, not on its peak.** The FRF changes with tool wear, with the workpiece as material is removed, and with spindle speed through gyroscopic and bearing effects. A cut placed exactly on a peak can drop off it.

**The FRF is specific to the tool, the holder and the machine together.** A lobe diagram measured with a different tool length is worthless, and that is the commonest way the analysis is misapplied.

---

## Measuring the transfer function

**A tap test with an instrumented hammer and an accelerometer at the tool tip**, giving the frequency response function directly.

| Element | Detail |
|---|---|
| Impact hammer | With a force transducer |
| Accelerometer | At the tool tip, or a laser vibrometer |
| Output | `G(omega)`, magnitude and phase |
| Time | Minutes |

**It takes minutes and it is almost never done**, which is why so much aerospace machining runs at a fraction of its capability. The analysis is cheap and the benefit is a factor of several in material removal rate.

**Thin walled workpieces have their own dynamics** and they change as material is removed. The workpiece FRF can dominate the tool FRF entirely on a thin wall, and it is a moving target through the cut. See [ThinWallMachining.md](ThinWallMachining.md).

---

## Design rules of thumb

| Rule | Value |
|---|---|
| `a_lim = -1/(2 K_s Re[G])` | The stability limit |
| Only the negative real part matters | Elsewhere it is unconditionally stable |
| Lobe peaks at `n = 60 f_c / (N k)` | |
| The first lobe is highest and widest | Prefer it |
| Factor of 3 to 5 available | Between arbitrary speed and a lobe peak |
| Tool stiffness goes as `1/L^3` | Shorten the overhang first |
| Stay inside the lobe, not on the peak | The FRF moves |
| The FRF is tool, holder and machine specific | Re-measure for each |

---

## Failure modes

**Chatter treated by reducing the depth of cut.** It works and it gives away the rate.

**Chatter treated by reducing the speed.** It may move into a worse region.

**Lobe diagram reused with a different tool length.** The FRF is different.

**Cut placed exactly on a lobe peak.** The FRF moves and it drops off.

**Workpiece dynamics ignored on a thin wall.** They dominate, and they change through the cut.

**FRF never measured.** The commonest case, and it costs a factor of several.

---

## Worked numbers

From [`MachiningProcess.calculateStabilityLobes`](../machiningProcessesLibrary/MachiningProcess.py), a 12 mm 4 flute end mill, 800 Hz natural frequency, 3 % damping:

| Material | Unconditional limit | Best lobe peak | Ratio |
|---|---|---|---|
| 6061-T6 | highest, `K_s` is lowest | several times higher | 3 to 5x |
| 316L | lower | several times higher | 3 to 5x |
| INCONEL 718 | lowest | several times higher | 3 to 5x |

**The ratio is roughly material independent** because `K_s` scales both the unconditional limit and the lobe peaks equally. The absolute depths differ by the specific energy ratio.

---

## Standards

| Standard | Scope |
|---|---|
| ISO 230 series | Test code for machine tools |
| ASME B5.54 | Performance evaluation of CNC machining centres |
| ISO 10816 | Mechanical vibration evaluation |
| ISO 8688 | Tool life testing in milling |

---

## Tool interface

```python
from MachiningProcess import MachiningProcess, CHATTER_LOBE_COUNT

machining = MachiningProcess()
machining.setInputs({'material': '6061', 'process': 'end mill',
                     'toolDiameter': 0.012, 'axialDepth': 0.005, 'radialDepth': 0.003,
                     'feedPerTooth': 0.0001, 'naturalFrequency': 800.0,
                     'dampingRatio': 0.03, 'modalStiffness': 2.0e7})
result = machining.calculateStabilityLobes()

print(f'unconditionally stable to {result["unconditionallyStable"]*1000:.2f} mm')
for lobe in result['lobes']:
    print(f'  lobe {lobe["lobeNumber"]}: {lobe["spindleSpeedRpm"]:7.0f} rpm, '
          f'{lobe["achievableDepth"]*1000:.2f} mm')
```

---

## References

1. Altintas, Y., *Manufacturing Automation: Metal Cutting Mechanics, Machine Tool Vibrations, and CNC Design*, 2nd ed., Cambridge University Press, 2012.
2. Tobias, S. A., *Machine Tool Vibration*, Blackie, 1965.
3. Schmitz, T. L. and Smith, K. S., *Machining Dynamics: Frequency Response to Improved Productivity*, 2nd ed., Springer, 2019.
