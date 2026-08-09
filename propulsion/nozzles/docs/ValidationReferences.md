[Home](../README.md) > Validation References

# Validation References

The external sources this sub-domain's tools are checked against, and the one thing they cannot check.

Kept separate from the reference lists at the foot of each document. Those are further reading; this is the material a test asserts against. The methodology is in [validation/README.md](../../../validation/README.md).

| Level | Means |
|---|---|
| **Hardware** | Compared against measured or specified performance of real hardware |
| **Standard** | Reproduces a published formula exactly. Catches an implementation error only |
| **Bounded** | No direct comparison, but the result is bracketed by something |
| **Unvalidated** | No external anchor. Recorded with what depends on it |

---

## The divergence efficiency relation

- **Source:** Standard result, in every nozzle text. `eta = (1 + cos alpha) / 2`
- **Validation level:** Standard
- **Relevance:** The only loss mechanism a contour designer controls directly, and the one every contour comparison rests on.
- **Key findings:**
  - A 15 degree cone gives 0.9830, the classical 1.7 per cent
  - An axial exit gives exactly 1.0, which is the sanity check on the implementation
  - The library reproduces the relation exactly and a test asserts the 15 degree value to four figures

## Summerfield and Schmucker separation criteria

- **Source:** Summerfield, Foster and Swan, *Flow separation in overexpanded supersonic exhaust nozzles*; Schmucker, *Flow processes in overexpanded chemical rocket nozzles*
- **Validation level:** Standard, and the two disagree
- **Relevance:** Both are curve fits to test data and neither is a physical limit. Which one is used changes the permitted area ratio by more than a third.
- **Key findings:**
  - Summerfield: separation at a fixed `Pe < 0.4 Pa`, permitting an area ratio of 21.42 at a 10 MPa chamber at sea level
  - Schmucker: `Pe / Pa = 0.667 (Pc / Pa)^-0.2`, permitting 29.17
  - **A 36 per cent difference in the permitted expansion**, and at an area ratio of 25 they disagree about whether the nozzle separates at all
  - Worth only 0.45 s of burn-averaged impulse, because the area ratio optimum is broad
  - The library reports both rather than picking one, and a test asserts they disagree at 25 so nobody later reconciles them

## Rao's wall angle chart

- **Source:** Rao, *Exhaust nozzle contour for optimum thrust*, Jet Propulsion 1958; the wall angle chart reproduced as Huzel and Huang figure 4-16
- **Validation level:** Standard, against a published chart, with a stated band
- **Relevance:** The exit wall angle sets the divergence loss, which is the largest of the three losses on every contour this sub-domain compares except a hundred per cent bell. It used to come from a lookup table.
- **Key findings:**
  - At an area ratio of 20 for an 80 per cent bell the chart gives an initial angle of about 33 degrees and an exit angle of about 11
  - The logarithmic fit gives 32.2 and 11.6, inside the registered band of one degree
  - **The band is not negligible.** A degree of exit angle is worth about 0.1 per cent of divergence efficiency at these angles
  - It is nonetheless a quarter of the error the lookup table it replaced was making, which was three and a half degrees
  - Registered as `CORRELATION_ACCURACY['raoWallAngles']`, because a tool cannot be validated to a tighter band than the correlation underneath it

**What the correction changed.** The table gave an 80 per cent bell 8 degrees regardless of area ratio. The divergence efficiency at 8 degrees is 0.9951 and at 11.5 it is 0.9899, so the table understated the divergence loss by a factor of two, and [NozzlePerformance](NozzlePerformance.md) concluded the boundary layer was the largest loss when it is not. **A published finding was withdrawn on the strength of this reference**, which is the clearest case in this repository of an external check earning its cost.

---

## RS-25, and what it cannot validate

- **URL:** <https://en.wikipedia.org/wiki/RS-25>
- **Accessed:** 09 August 2026, carried forward from the propulsion hub validation
- **Validation level:** Bounded, and the boundary is the finding
- **Relevance:** The obvious check on a thrust coefficient loss model is a real engine's delivered performance. It does not work, and the reason is worth recording.
- **Key findings:**
  - A published specific impulse is the product of c\* efficiency and thrust coefficient efficiency, and **nothing published separates them**
  - RS-25's combined efficiency against the hub's ideal is 0.9837
  - Splitting that at a c\* efficiency of 0.985, 0.99 or 1.00 gives implied Cf efficiencies of 0.999, 0.994 and 0.984, and **every one of them is physically admissible**
  - So the loss decomposition cannot be validated against it without assuming the split, and assuming the split is what makes the check circular
  - A test records this limit explicitly, so it does not get quietly claimed as a validation later

**What the data can do.** A thrust coefficient efficiency above one is impossible, so RS-25's c\* efficiency must be at least 0.9837. That is a real inference, and it is another confirmation that the hub's 0.96 default is conservative for a best-in-class engine.

**What the comparison bounds.** At RS-25's area ratio the decomposition gives 0.980 against a lowest admissible implied value of 0.984. The decomposition is therefore conservative, by between half a point and two and a half depending on the split. Conservative is the right direction, and the width of that range is the honest measure of what the check is worth.

---

## What is not validated

**The boundary layer and kinetic loss coefficients.** One per cent and half a per cent respectively, scaled by contour length and by the logarithm of area ratio. They are representative rather than sourced. Their sum reproduces the propulsion hub's single 0.98, which is a consistency check between two parts of this repository and not an external one.

**The altitude compensation recovery fractions.** What fraction of the ideal benefit each arrangement captures: 55 per cent for an extendible nozzle, 45 for a dual bell, 70 for an aerospike. These encode an ordering and they are not predictions for a specific device.

**The mass penalties** for the same arrangements, on the same basis.

**The wetted area.** Published engines give channel counts and coolant paths rather than wetted areas, so neither the cone frustum estimate nor the integrated Rao contour has an external anchor. Only their ratio is being claimed, 1.097 on the reference booster, and it is registered as `bellWettedArea` with what depends on it: [combustionDevices](../../combustionDevices/docs/RegenerativeCooling.md) sizes its cooling circuit on the frustum and therefore understates the total wetted area by about 6.6 per cent.

**The bound itself is computed rather than assumed**, and it is the part of the altitude compensation document that does not depend on any of the above. That 14.5 s is a property of the ascent profile and the chamber pressure, not of a model of any device.
