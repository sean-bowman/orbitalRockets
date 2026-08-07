[Home](../README.md) > Fracture and Damage Tolerance

# Fracture and Damage Tolerance

## Contents

- [Overview](#overview)
- [The governing equation](#the-governing-equation)
- [Critical flaw size](#critical-flaw-size)
- [Leak before burst](#leak-before-burst)
- [Proof testing as an inspection](#proof-testing-as-an-inspection)
- [Fatigue crack growth](#fatigue-crack-growth)
- [The threshold](#the-threshold)
- [Initial flaw size](#initial-flaw-size)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Damage tolerance starts from an assumption that is uncomfortable and correct: **the part already contains a crack.** Not might contain one, does contain one, at the largest size the inspection method could have missed.

Everything else follows. Given that crack, is the part safe now, and will it still be safe after the service life?

The alternative philosophy, safe life, assumes the part is flawless and retires it before a crack could initiate. It is used where inspection is impossible, and it is expensive because the retirement life carries a large scatter factor.

---

## The governing equation

```
K = Y sigma sqrt(pi a)
```

`K` is the stress intensity factor, `Y` a geometry factor, `sigma` the remote stress and `a` the flaw depth. The part fails when `K` reaches the material's fracture toughness `K_Ic`.

| Geometry | Y |
|---|---|
| Through crack, infinite plate | 1.00 |
| **Surface flaw, semi-elliptical** | **1.12** |
| Corner crack at a hole | 1.20 |
| Embedded flaw | 1.00 |

**The 1.12 free surface correction is the usual case**, because surface flaws are what inspection finds and what service produces.

**Linear elastic fracture mechanics requires small scale yielding.** The plastic zone at the crack tip has to be small compared with the crack and the remaining ligament. Above about 90 percent of yield the assumption fails and an elastic-plastic method is needed.

**Plane strain requires thickness.** The criterion is `t >= 2.5 (K_Ic / F_ty)^2`. Below that the part is in plane stress, where the effective toughness is higher than `K_Ic`, so using `K_Ic` is conservative but the critical flaw is understated.

---

## Critical flaw size

Inverting at `K = K_Ic`:

```
a_critical = (1 / pi) (K_Ic / (Y sigma))^2
```

**The inverse square dependence on stress is the whole story.** Halving the stress quadruples the tolerable flaw. A lightly stressed vessel is easy to fracture control and a highly stressed one is not, and no amount of inspection changes that relationship.

**It also means the toughness matters more than it appears to.** A 33 percent toughness gain is a 78 percent larger critical flaw, which is why ELI titanium is specified for fracture critical parts and why the STA condition is usually the wrong choice.

| Ti-6Al-4V at 524 MPa | K_Ic | a_critical |
|---|---|---|
| **Annealed** | 75 MPa-sqrt(m) | **5.19 mm** |
| STA | 49 MPa-sqrt(m) | 2.22 mm |
| ELI annealed | 100 MPa-sqrt(m) | 9.22 mm |

---

## Leak before burst

**When the critical flaw depth exceeds the wall thickness, a growing crack penetrates the wall and vents before it reaches the length that would cause unstable fracture.** The vessel leaks, the leak is detectable, and the failure is not a fragmentation event.

```
leak before burst  <=>  a_critical > t_wall
```

This is a design criterion worth paying mass for on any pressure vessel near people or near flight hardware, and it is a property of the stress and the material together rather than of either alone.

**When it is not satisfied**, the vessel can fail unstably from a flaw that has not yet penetrated the wall, so there is no leak to detect first. That demands either lower stress, a tougher material, or a fracture control programme relying entirely on inspection.

**The criterion is what makes the annealed versus STA titanium decision.** The bottle in the worked example has a 2.62 mm wall. Annealed gives a 5.19 mm critical flaw and leaks before it bursts; STA gives 2.22 mm and does not. **The stronger heat treatment makes the vessel less safe**, and nothing in a strength table shows that.

---

## Proof testing as an inspection

This is the idea that makes proof testing a fracture control method rather than merely a strength demonstration.

**A part that survives proof cannot contain a flaw larger than the critical size at proof stress.** Since proof stress exceeds operating stress, that screened flaw is smaller than the one critical in service:

```
a_screened / a_critical = (sigma_operating / sigma_proof)^2
```

At a 1.5 proof factor that ratio is `1/2.25`, so **the proof test guarantees the absence of any flaw larger than 44 percent of the critical size.** That is a real, quantified margin bought by the test.

**It is a 100 percent inspection with a credited flaw size, applied to every article, using the article itself as the instrument.** No NDE method comes close on coverage.

**The catch is that proof testing can also grow a flaw.** A part with a subcritical flaw is loaded to a high stress intensity during the test, and in a material susceptible to sustained load cracking or in a corrosive environment the test itself can extend the crack. This is why proof media, hold time and environment are controlled.

The test side of this is in [fluidSystemsTesting ProofAndBurstTesting.md](../../fluidSystems/fluidSystemsTesting/docs/ProofAndBurstTesting.md).

---

## Fatigue crack growth

Between the initial flaw and the critical size, the crack grows under cyclic load.

```
da/dN = C (dK)^m          dK = Y d_sigma sqrt(pi a)
```

**A units trap worth flagging.** The Paris coefficient `C` is quoted for `dK` in MPa-sqrt(m) in every published da/dN table, while a base SI codebase carries Pa-sqrt(m). Feeding Pa-sqrt(m) into a power law with `m` near 3.3 overstates the growth rate by twenty orders of magnitude and returns zero life. The conversion has to happen once, deliberately, and there is a test in this domain that exists because that bug was written.

**Typical exponents:**

| Material | m | C (MPa-sqrt(m), m/cycle) |
|---|---|---|
| Aluminium 2xxx / 7xxx | 3.1 to 3.5 | 1.4e-11 to 2.8e-11 |
| Titanium | 3.2 to 3.4 | 4.2e-12 to 7.0e-12 |
| Austenitic stainless | 3.2 | 2.8e-12 to 3.2e-12 |
| Nickel alloys | 3.1 | 3.0e-12 to 5.0e-12 |
| Low alloy steel | 3.0 | 6.9e-12 |

**Integrate numerically rather than in closed form**, because the closed form assumes `Y` is constant and it stops being usable as soon as the flaw approaches the wall.

**A scatter factor of four on life is conventional** for a safe life analysis, matching the four times life factor used in [fluidSystemsTesting LifeAndEnduranceTesting.md](../../fluidSystems/fluidSystemsTesting/docs/LifeAndEnduranceTesting.md).

---

## The threshold

**Below a threshold stress intensity range, cracks do not grow at all.**

```
sigma_threshold = dK_th / (Y sqrt(pi a))
```

| Material | dK_th at R = 0.1 |
|---|---|
| Aluminium 7xxx | 2.5 MPa-sqrt(m) |
| Aluminium 2xxx | 2.9 MPa-sqrt(m) |
| Titanium | 4.0 to 4.8 MPa-sqrt(m) |
| **Austenitic stainless** | **6.0 to 6.5 MPa-sqrt(m)** |
| Inconel 718 | 8.0 MPa-sqrt(m) |

**A part held below the threshold has unlimited life by this mechanism**, which is a far stronger statement than any finite cycle count. On a pressure vessel that cycles many thousands of times it is often the criterion worth designing to, and it is worth checking before spending effort on a crack growth integration.

The threshold falls as the stress ratio rises, so a component with a high mean stress has less margin than the `R = 0.1` value suggests.

---

## Initial flaw size

Per NASA-STD-5009, the initial flaw is what the inspection method is **credited** with finding, not what it typically finds.

| Method | Credited depth | Credited length |
|---|---|---|
| **Penetrant, standard** | **0.64 mm** | 1.27 mm |
| Penetrant, special procedure | 0.38 mm | 0.76 mm |
| Eddy current | 0.51 mm | 1.02 mm |
| Ultrasonic, contact | 1.90 mm | 3.81 mm |
| **Radiography** | 2.54 mm | 5.08 mm |
| **Computed tomography** | **0.25 mm** | 0.51 mm |

**Radiography is effectively blind to a tight planar crack normal to the beam**, which is the dangerous orientation. Its credited size reflects that, and it is why RT alone is not a fracture control inspection for a crack-critical part.

**Computed tomography is the only practical volumetric method for an additive internal passage**, and it is why additive fracture critical hardware is expensive to inspect.

**The governing initial flaw is the smaller of the NDE credit and the proof screen.** Where proof screens to a smaller flaw than the NDE credits, the proof test is the inspection.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Assume the part already contains a crack | At the credited NDE size |
| Critical flaw goes as `1/sigma^2` | Halve the stress, quadruple the tolerable flaw |
| Leak before burst when `a_critical > t_wall` | Worth paying mass for |
| Proof at 1.5x screens to 44 % of the critical flaw | A 100 percent inspection |
| LEFM needs stress below ~0.9 yield | And adequate thickness for plane strain |
| Life scatter factor | 4x, conventionally |
| Below the threshold, life is unlimited | Check this before integrating |
| Paris C is quoted in MPa-sqrt(m) | Convert once, deliberately |
| A tougher condition may beat a stronger one | Critical flaw goes as toughness squared |

---

## Failure modes

**A fracture critical part with no toughness data.** It cannot be analysed and assuming a value is worse than refusing.

**Sizing on strength and ignoring toughness.** The STA titanium case: stronger, and no leak before burst.

**Radiography credited as a crack inspection.** Blind to the dangerous orientation.

**LEFM applied above yield.** The small scale yielding assumption has failed.

**A units error in the Paris law.** Twenty orders of magnitude, and it returns zero life.

**Proof testing growing the flaw it was meant to screen.** Sustained load cracking during the hold.

**An initial flaw taken as what inspection typically finds.** The credited size is larger, deliberately.

---

## Worked example

From [`codeInterface.py`](../codeInterface.py), the Ti-6Al-4V bottle at 524.4 MPa membrane stress with a 2.62 mm wall:

| Quantity | Value |
|---|---|
| K_Ic, annealed | 75 MPa-sqrt(m) |
| **Critical flaw at MEOP** | **5.19 mm** |
| Wall thickness | 2.62 mm |
| **Leak before burst** | **Satisfied, ratio 1.98** |
| Proof screens flaws to | 2.31 mm |
| Penetrant credited with | 0.64 mm, which governs |
| **Cycles to failure** | **2873 against 500 required** |
| Life margin | 5.7x, against the 4x conventionally required |

**The same bottle in the STA condition** has a critical flaw of 2.22 mm against the same 2.62 mm wall, so it loses leak before burst entirely despite being 17 percent stronger.

---

## Standards

| Standard | Scope |
|---|---|
| **NASA-STD-5009** | Nondestructive evaluation requirements for fracture critical components |
| **NASA-STD-5019** | Fracture control requirements for spaceflight hardware |
| **AIAA S-080** | Metallic pressure vessels, including fracture control |
| ASTM E399 | Plane strain fracture toughness of metallic materials |
| **ASTM E647** | Measurement of fatigue crack growth rates |
| ASTM E1820 | Measurement of fracture toughness (J and CTOD) |
| ASTM E1823 | Terminology relating to fatigue and fracture testing |
| **NASGRO / AFGROW** | The crack growth analysis codes used in practice |
| Damage Tolerant Design Handbook | CINDAS, the da/dN and K_Ic data source |
| MIL-STD-1530 | Aircraft structural integrity programme |

---

## Tool interface

```python
from DamageTolerance import DamageTolerance

damage = DamageTolerance()
damage.setInputs({'material': 'Ti-6Al-4V', 'condition': 'annealed',
                  'operatingStress': 524.4e6, 'proofStress': 786.6e6,
                  'wallThickness': 0.00262, 'designCycles': 500,
                  'inspectionMethod': 'penetrant, standard',
                  'geometryCase': 'surface flaw, semi-elliptical'})

damage.calculateCriticalFlaw()      # and the plane strain thickness check
damage.checkLeakBeforeBurst()
damage.calculateProofScreening()    # what the proof test guarantees is absent
damage.calculateCrackGrowth()       # Paris integration to the critical size
damage.calculateThresholdStress()   # below which life is unlimited
print(damage.generateReport())
```

Lookup tables: `DamageTolerance.GEOMETRY_FACTORS`, `DamageTolerance.NDE_FLAW_SIZES`.

---

## References

1. NASA-STD-5019A, *Fracture Control Requirements for Spaceflight Hardware*.
2. NASA-STD-5009B, *Nondestructive Evaluation Requirements for Fracture-Critical Metallic Components*.
3. Anderson, T. L., *Fracture Mechanics: Fundamentals and Applications*, 4th ed., CRC Press, 2017.
4. Damage Tolerant Design Handbook, CINDAS/USAF, Volumes 1 to 4.
5. Paris, P. and Erdogan, F., "A Critical Analysis of Crack Propagation Laws", *Journal of Basic Engineering*, Vol. 85, 1963.
