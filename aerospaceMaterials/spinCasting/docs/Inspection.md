[Home](../README.md) > Inspection

# Inspection

## Contents

- [Overview](#overview)
- [Radiography](#radiography)
- [Ultrasonic](#ultrasonic)
- [Penetrant](#penetrant)
- [Dimensional](#dimensional)
- [Metallography](#metallography)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [References](#references)

---

## Overview

A centrifugal casting is a good inspection subject: the geometry is simple, both surfaces are accessible after machining, and the wall is uniform. That is unusual among castings and it is worth exploiting.

---

## Radiography

**The primary volumetric method for castings**, and it works well here because the geometry is simple.

| Advantage | Detail |
|---|---|
| **Uniform wall** | A single exposure setting covers the whole part |
| **Simple geometry** | No section changes to confuse the interpretation |
| **Volumetric coverage** | Gas porosity and shrinkage both show clearly |

**Reference radiographs are the acceptance basis**, per ASTM E446, E186 or E280 depending on section thickness. The casting is compared against a graded set of standard images and assigned a severity level per defect type.

**Radiography sees rounded defects well** and it sees planar ones poorly, which is the opposite of what matters in an additive part and it suits a casting where gas and shrinkage dominate.

---

## Ultrasonic

| Use | Notes |
|---|---|
| **Wall thickness** | Fast, accurate, and it maps the whole part |
| **Laminar defects** | Well suited, because they are normal to the beam |
| Coarse grain attenuation | The limitation |

**Coarse columnar structure attenuates and scatters the beam**, which is the specific difficulty with centrifugal castings. The columnar grains are radial, meaning aligned with a normal-incidence beam, and that is close to the worst case for scattering.

**Lower frequency helps** at the cost of resolution, and a heat treated equiaxed structure inspects far better than an as-cast columnar one. **Inspect after the normalising treatment where possible.**

---

## Penetrant

**Surface breaking defects, and it needs a machined surface.**

| Surface | Suitability |
|---|---|
| As-cast bore | **Unusable.** Rough and oxidised; it indicates everywhere |
| Machined bore | Good |
| As-cast outer | Marginal |
| Machined outer | Good |

**Machine before penetrant.** This is the practical reason the sequence puts bore roughing before inspection. See [PostProcessing.md](PostProcessing.md).

---

## Dimensional

| Measurement | Method |
|---|---|
| **Wall thickness** | Ultrasonic, mapped |
| **Concentricity** | Between bore and outer, which the process does well |
| Ovality | Low, by the nature of the process |
| Length and squareness | Conventional |

**Wall thickness mapping is the most informative dimensional check** because it directly shows a taper from a bad pour or an eccentricity from non-uniform cooling.

---

## Metallography

| Purpose | Notes |
|---|---|
| **Structure** | Chill, columnar and equiaxed zones, and their extents |
| **Inclusion content** | Per ASTM E45, and it is the direct check on the process benefit |
| **Grain size** | Per ASTM E112 |
| Segregated layer depth | Direct measurement, on a sectioned coupon |

**Sectioning a first article and measuring the segregated layer directly is the only way to confirm the machining allowance.** Everything else is inference from a model.

**Inclusion counts at the bore and at mid-wall, compared, are the direct evidence that the process did what it was chosen for.** A casting with the same inclusion count at both is a casting where the separation did not happen.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Radiography is the primary volumetric method | Simple geometry suits it |
| Reference radiographs are the acceptance basis | ASTM E446, E186, E280 |
| Ultrasonic is attenuated by columnar structure | Inspect after normalising |
| Penetrant needs a machined surface | The as-cast bore is unusable |
| Map the wall thickness | It shows taper and eccentricity |
| Section a first article | The only direct check on the allowance |
| Compare inclusion counts bore against mid-wall | The direct evidence |

---

## Failure modes

**Penetrant on an as-cast bore.** Indications everywhere.

**Ultrasonic on an as-cast columnar structure.** Attenuated, and defects missed.

**Wall thickness checked at one point.** Taper and eccentricity missed.

**Segregated layer depth taken from a model.** Never confirmed.

**Radiography acceptance level not specified.** No basis for accept or reject.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM E446** | Reference radiographs for steel castings up to 2 in |
| ASTM E186 | Heavy walled steel castings, 2 to 4.5 in |
| ASTM E280 | Heavy walled steel castings, 4.5 to 12 in |
| ASTM E1417 | Liquid penetrant testing |
| ASTM E114 | Ultrasonic pulse-echo straight beam |
| ASTM E797 | Ultrasonic thickness measurement |
| ASTM E45 | Inclusion content of steel |
| ASTM E112 | Determining average grain size |
| ASTM A802 | Steel castings, surface acceptance standards |

---

## References

1. ASM Handbook Volume 17, *Nondestructive Evaluation and Quality Control*.
2. Campbell, J., *Complete Casting Handbook*, 2nd ed., Butterworth-Heinemann, 2015.
3. ASTM E446, *Standard Reference Radiographs for Steel Castings Up to 2 in. in Thickness*.
