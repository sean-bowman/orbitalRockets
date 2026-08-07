[Home](../../README.md) > Welds

# Welds

## Contents

- [Overview](#overview)
- [Processes](#processes)
- [Joint designs](#joint-designs)
- [Joint efficiency and code derating](#joint-efficiency-and-code-derating)
- [Heat affected zone](#heat-affected-zone)
- [Solidification cracking and ferrite control](#solidification-cracking-and-ferrite-control)
- [Purge and root quality](#purge-and-root-quality)
- [Distortion and residual stress](#distortion-and-residual-stress)
- [Inspection](#inspection)
- [Qualification](#qualification)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Operations](#operations)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A weld is the best joint available in a fluid system. It has the lowest leak rate, the lowest pressure drop, the lowest mass and the fewest failure modes of any option. It is also permanent, which means every welded joint is a commitment and the design has to be right before the torch is struck.

Three questions govern the design:

1. **How much strength is left?** A weld is not parent metal. The code joint efficiency `E` accounts for the fabrication process and inspection level, and the heat affected zone knockdown accounts for what the thermal cycle did to the base material. For 6061-T6 aluminum in a socket joint the two together remove more than half the strength.
2. **Will it crack?** Austenitic stainless welds solidify with a ferrite content that depends on composition. Too little and the joint hot-cracks during solidification; too much and it embrittles at cryogenic temperature.
3. **What inspection is required?** Set by the pressure class, the fluid hazard and the governing code, and constrained by whether the joint geometry can be volumetrically inspected at all.

---

## Processes

| Process | Where used | Advantages | Limitations |
|---|---|---|---|
| **GTAW manual** | Repair, one-offs, complex geometry | Universal, high quality in skilled hands | Operator dependent; qualification travels with the welder |
| **GTAW orbital (automatic)** | Tube-to-tube and tube-to-fitting in clean systems | Highly repeatable, documented parameters, no filler needed for thin wall | Requires precise, square, burr-free tube ends and consistent fit-up |
| **GMAW** | Structure, thick section | Fast deposition | Spatter and lower cleanliness. Rarely used on fluid systems |
| **Electron beam** | Precision joints in thick or precipitation-hardened material | Very narrow HAZ, deep single-pass penetration, minimal distortion | Requires a vacuum chamber that fits the part |
| **Laser beam** | Thin section, high speed, automated | Narrow HAZ, low distortion, no vacuum required | Tight fit-up tolerance; reflectivity issues in aluminum and copper |
| **Friction stir** | Large aluminum tank barrels and domes | No melting, so no solidification cracking; much less strength loss in aluminum | Heavy backing support required; leaves an exit hole to design out |
| **Resistance / capacitive discharge** | Small attachments, thermocouples | Very local heat input | Not a pressure boundary process |
| **Brazing** | Dissimilar metals, complex assemblies, heat exchangers | Joins materials that cannot be fusion welded; low distortion | Filler melting point limits service temperature; joint strength depends on gap control |

**Autogenous versus filler.** An autogenous weld (no filler) is the standard for thin-wall tube-to-tube joints because it eliminates a variable and there is no room for filler anyway. It has a consequence: the weld metal composition is the parent composition, so the ferrite balance is whatever the tube supplier delivered. Filler metal exists partly so that the weld composition can be controlled independently of the base metal, and giving that up means the tube chemistry has to be right.

---

## Joint designs

| Joint | E | Volumetrically inspectable | K_t | Notes |
|---|---|---|---|---|
| **Butt, full penetration, radiographed** | 1.00 | Yes | 1.2 | The reference joint |
| Butt, full penetration, visual only | 0.85 | No | 1.2 | Same joint, 15 % of allowable stress paid for skipping the RT |
| **Tube to fitting (orbital)** | 1.00 | Yes | 1.3 | The workhorse of a clean fluid system |
| Sleeve | 0.85 | No | 1.8 | Field repair joint; internal crevice |
| **Socket** | 0.80 | No | 2.1 | Fast fit-up, permanent internal crevice |
| Fillet | 0.60 | No | 2.5 | Structural attachments only |
| Electron beam | 1.00 | Yes | 1.1 | Narrowest HAZ |
| Friction stir | 0.95 | Yes | 1.2 | Aluminum tank barrels |

**The critical distinction is volumetric inspectability.** A full penetration butt weld with a back purge can be radiographed or ultrasonically inspected and can carry `E = 1.0`. A socket weld or a fillet weld cannot be volumetrically inspected at all, so it carries a permanent efficiency penalty and a fatigue penalty regardless of how well it was made.

**The socket weld crevice.** A socket joint leaves an unwelded annular gap at the root between the tube OD and the socket bore. That crevice:

- traps fluid, which cannot be flushed out and becomes a contamination and passivation problem
- cannot be inspected by any method
- is a crack initiation site under thermal cycling, because the tube and the socket expand differentially and the gap root is a sharp notch
- is a crevice corrosion site in any system that sees moisture

Socket welds are fast and forgiving to fit up, which is why they are common on ground systems. They should not be used in a fatigue-critical, cleanliness-critical or flight pressure boundary.

---

## Joint efficiency and code derating

Two independent derating mechanisms apply and they **multiply**:

```
S_weld = min( 2/3 * yield_HAZ,  ultimate_HAZ / 3.5 ) * E
```

**Joint efficiency `E`** is a code factor, not a material property. It is a statement about how confident the code is that the joint has no undetected flaws, and it depends on the joint geometry and the inspection level. ASME B31.3 Table A-1B and Table 302.3.4 give the values.

**HAZ knockdown** is what the thermal cycle did to the base metal:

| Material | Yield factor | Ultimate factor | Recoverable by PWHT? |
|---|---|---|---|
| 304L, 316L, 321 | 1.00 | 1.00 | N/A (nothing lost) |
| Inconel 625 | 1.00 | 1.00 | N/A |
| Monel 400 | 1.00 | 1.00 | N/A |
| Ti-6Al-4V | 0.90 | 0.95 | Yes |
| **Inconel 718** | **0.55** | **0.70** | **Yes** (solution and age after welding) |
| **6061-T6** | **0.55** | **0.65** | **No, practically** |
| **7075-T73** | **0.40** | **0.50** | **No. Not weldable** |

**The aluminum case is the one that catches people.** 6061-T6 is a precipitation hardened alloy. The weld thermal cycle dissolves and over-ages the strengthening precipitates in a band either side of the weld, and the as-welded HAZ properties are close to the annealed (O temper) condition. It does not recover on its own, and a post-weld solution treat and age requires taking the whole assembly to 530 degC and quenching it, which distorts anything of consequence. **The as-welded HAZ properties are the design properties for a welded 6061 structure.**

A 6061-T6 socket weld therefore carries `0.80 x 0.55 = 0.44` of the parent metal capability, and a design that used parent metal properties is wrong by a factor of 2.3.

**Inconel 718 is recoverable but the sequence matters.** Weld in the solution annealed condition, then solution treat and age the whole assembly. Welding 718 in the aged condition risks strain age cracking, where the residual stress from welding drives cracking during the subsequent heat-up through the aging range.

---

## Heat affected zone

Beyond strength, the HAZ has three other failure mechanisms worth knowing.

**Sensitization in austenitic stainless.** Between roughly 700 and 1150 K, chromium carbides precipitate at grain boundaries in the HAZ, depleting the adjacent metal of chromium and destroying its corrosion resistance. The result is intergranular attack in service. Three mitigations:

- **Low carbon grades (304L, 316L).** Below 0.03 percent carbon there is not enough carbon to form significant carbides in a normal weld thermal cycle. This is why every fluid system uses the L grades and it is the standard answer.
- **Stabilized grades (321, 347).** Titanium or niobium ties up the carbon preferentially. Preferred where the joint sees 700 to 1150 K in service, not just during welding.
- **Post-weld solution anneal.** Effective, impractical on an assembly.

**Grain growth.** The region immediately adjacent to the fusion line sees the highest temperature and grows coarse grains, which reduces toughness. Minimized by low heat input, which is one of the arguments for electron beam and laser welding.

**Hydrogen embrittlement in ferritic and martensitic steels.** Hydrogen from moisture in the arc atmosphere or on the surface diffuses into the HAZ and causes delayed cracking hours or days after welding. Not a problem for austenitic stainless (the austenite lattice holds hydrogen but does not embrittle the same way) but a serious problem for high-strength steels. Preheat and low-hydrogen practice are the mitigations.

**Titanium contamination.** Titanium picks up oxygen, nitrogen and hydrogen readily above about 500 degC and the pickup is irreversible embrittlement. Welding titanium requires full inert shielding of the weld pool, the HAZ **and the back side**, usually with a trailing shield and a purge chamber. **Weld colour is the inspection:** bright silver or light straw is acceptable, dark blue is marginal, grey or white is a reject. There is no repair; the contaminated metal must be removed.

---

## Solidification cracking and ferrite control

Austenitic stainless weld metal can solidify in two modes, and the mode determines whether it cracks.

**Fully austenitic solidification** concentrates sulfur and phosphorus in the last liquid to freeze. Those elements form low-melting films along the grain boundaries, and the contraction strain of solidification tears them open. This is hot cracking, or solidification cracking, and it is a centreline crack that runs the length of the weld.

**Primary ferritic solidification** avoids it: delta ferrite has a much higher solubility for sulfur and phosphorus, so the low-melting films do not form. A small amount of retained delta ferrite in the finished weld is the signature that solidification went the right way.

**Ferrite number targets:**

| FN | Consequence |
|---|---|
| < 3 | Solidification cracking risk |
| **3 to 8** | **The design window for cryogenic service** |
| 3 to 10 | The general design window |
| > 10 | Reduced cryogenic toughness; sigma phase embrittlement risk at elevated temperature |

**Prediction: the WRC-1992 diagram.**

```
Cr_eq = Cr + Mo + 0.7*Nb
Ni_eq = Ni + 35*C + 20*N + 0.25*Cu
```

with the ferrite number read from the diagram. Nominal ER316L filler (18.5 Cr, 12 Ni, 2.5 Mo, 0.02 C, 0.05 N) gives `Cr_eq = 21.0`, `Ni_eq = 13.8` and roughly FN 5, which is squarely in the window. That is not an accident: filler metals are deliberately over-alloyed in chromium relative to the base metal precisely to land there.

**Why ferrite is bad in the other direction.** Ferrite is body-centred cubic and has a ductile-to-brittle transition temperature; austenite is face-centred cubic and does not. A high ferrite weld in a cryogenic joint has a brittle phase distributed through it, and the joint toughness falls. At elevated temperature (roughly 850 to 1150 K) ferrite transforms to sigma phase, which is hard, brittle and destroys both toughness and corrosion resistance.

**Measure it, do not just predict it.** A Feritscope reading on the procedure qualification coupon takes a minute and the diagram is only a prediction.

---

## Purge and root quality

**The back purge is not optional on a fluid system weld.**

When stainless steel, nickel alloys or titanium are welded, the root of the weld is molten metal exposed to whatever atmosphere is on the inside of the joint. If that atmosphere contains oxygen, the root oxidizes. The result, called **sugaring**, is a rough, crystalline, heavily oxidized internal surface.

Consequences of a sugared root, in order of how much they matter:

1. **Particle shedding.** The oxide is friable and it comes off into the flow. In an oxygen system a shed particle in a high-velocity stream is an ignition source. In any system it plugs orifices and damages valve seats.
2. **Crack initiation.** The rough oxidized surface is a notch field on the inside of the pressure boundary, exactly where the hoop stress is highest.
3. **Corrosion.** The chromium-depleted oxidized layer has no corrosion resistance.
4. **Cleanability.** A sugared surface cannot be cleaned to any meaningful level.

**Purge practice:**

- Argon (or argon-hydrogen for austenitic stainless, which is more reducing) inside the joint, displacing air before the arc is struck.
- Oxygen content below 50 ppm for stainless; below 20 ppm is better. **Below 10 ppm for titanium.**
- Verify with an oxygen analyser, not by purge time. Purge time depends on volume, geometry and flow rate, and dead legs hold air.
- Purge dams for large volumes, so the whole system does not have to be filled with argon.
- Maintain the purge until the weld has cooled below the oxidation temperature, which for stainless is roughly 700 K.

**Root reinforcement and suck-back.** Too much heat input pulls the root through (excessive reinforcement into the bore, which restricts flow and creates a particle trap), and too little leaves concavity or lack of penetration. On an orbital weld this is a parameter development problem; on a manual weld it is a skill problem. Either way it is a borescope inspection item.

---

## Distortion and residual stress

Welding is a highly localized thermal cycle in a constrained structure, and it leaves both distortion and residual stress.

**Distortion** matters for fit-up and alignment. A tube welded into a fitting at one end and constrained at the other will pull. Mitigations: balanced welding sequence, tack welds, fixturing, lower heat input, and where possible welding before final machining of critical interfaces.

**Residual stress** matters for fatigue and for stress corrosion cracking. As-welded residual stress at the weld toe can approach the yield strength of the material, which means the mean stress in a fatigue calculation is far higher than the applied load suggests. Mitigations:

- Post-weld stress relief (effective, but a full thermal cycle on an assembly)
- Weld toe dressing (grinding the toe to remove the notch and the surface residual tension)
- Shot peening or laser peening (puts the surface into compression)
- Designing the joint so the toe is not at the highest stress location

For austenitic stainless in a chloride environment, residual tensile stress plus chloride plus temperature is the classic recipe for stress corrosion cracking. A launch site is a chloride environment.

---

## Inspection

| Method | Finds | Misses |
|---|---|---|
| **Visual** | Surface geometry, undercut, overlap, gross defects, weld colour | Everything subsurface |
| **Liquid penetrant (PT)** | Surface-breaking cracks and porosity | Anything not open to the surface |
| **Radiography (RT)** | Volumetric defects: porosity, slag, incomplete fill, lack of fusion at some orientations | **Tight planar cracks aligned with the beam.** This is the important gap |
| **Ultrasonic (UT)** | Planar defects, lack of fusion, cracks | Requires a trained operator and a calibration block. Difficult on thin wall and on coarse-grained austenitic weld metal |
| **Leak test** | Through-thickness defects only | Everything that has not yet grown through the wall |
| **Borescope** | Internal root condition, sugaring, suck-back, spatter | Anything not on the inside surface |

**Radiography and ultrasonic examination find different things,** and this is the point most often missed. RT sees volumetric defects well and tight cracks poorly, because a crack aligned with the beam presents almost no absorption difference. UT is the reverse. Where a missed crack matters, specify both, or specify RT plus PT so surface-breaking cracks are caught by the penetrant.

**Required inspection level, typical aerospace practice:**

| Service | Inspection |
|---|---|
| Non-pressure structural attachment | Visual |
| Pressure boundary, non-hazardous, below 10 MPa | Visual + PT |
| Pressure boundary, hazardous fluid (toxic, flammable, oxidizer) | Visual + PT + RT (or UT) |
| Pressure boundary above 10 MPa | Visual + PT + RT (or UT) |
| Oxygen service | All of the above **plus borescope of the root** |
| Any joint that cannot be volumetrically inspected, in a service that requires it | **Change the joint design** |

That last row is the design action, not an inspection plan. If the service requires volumetric inspection and the joint geometry does not permit it, the answer is a full penetration butt or tube-to-fitting weld, not a waiver.

---

## Qualification

Three things are qualified, and all three are required:

**1. The weld procedure specification (WPS).** The documented set of parameters: process, material, thickness range, position, filler, gas, purge, current, voltage, travel speed, preheat, interpass temperature, post-weld heat treatment. Supported by a **procedure qualification record (PQR)**, which is the test data from destructively testing a coupon welded to that procedure. ASME Section IX and AWS D17.1 define the required tests: tensile, bend, and for some applications impact and macro-etch.

**2. The welder or operator.** A welder is qualified to a procedure, within ranges (material group, thickness, position, diameter). Qualification lapses if the welder does not use the process for a defined period. For orbital welding the "welder" is the machine plus the operator, and the qualification includes the specific weld head and power supply.

**3. The equipment and consumables.** Filler metal lot traceability, gas purity certification, equipment calibration.

**Production coupons.** For critical work, a coupon welded at the same time, with the same setup, by the same operator, on the same material lot, and destructively tested. This is the only direct evidence about the actual production weld, and it is why orbital welding programs run a coupon at the start of every shift and after every parameter change.

---

## Design rules of thumb

| Rule | Value | Why |
|---|---|---|
| Weld rather than fitting wherever permanent | Always | Best leak, mass, dP, and no torque control |
| E and HAZ knockdown multiply | `S = S_HAZ * E` | A 6061 socket weld is 0.44 of parent |
| 6061-T6 as-welded HAZ | ~55 % of yield | Not recoverable in a practical assembly |
| Use L-grade stainless | 304L, 316L | Sensitization resistance |
| Use stabilized grades for hot service | 321, 347 | 700 to 1150 K service |
| Ferrite number target | FN 3 to 8 cryogenic, 3 to 10 general | Hot cracking below, embrittlement above |
| Back purge oxygen | < 50 ppm stainless, < 10 ppm titanium | Sugaring |
| Purge verification | By analyser, not by time | Dead legs hold air |
| No welds in high-stress bends | Always | The toe notch stacks on the bend stress |
| Weld access | Torch access plus inspection access | Retrofitting either is impossible |
| Titanium weld colour | Silver or light straw only | Colour is the contamination inspection |
| Socket welds | Not in flight pressure boundary | Uninspectable crevice, K_t 2.1 |
| Fatigue on a K_t > 1.5 joint above 1000 cycles | Needs a fatigue assessment | Static strength is not the failure mode |

---

## Failure modes

**Solidification (hot) cracking.** Centreline crack the length of the weld. Caused by fully austenitic solidification, high sulfur or phosphorus, or excessive restraint. Fixed by filler selection to raise the ferrite number.

**Sugared root.** Oxidized, particle-shedding internal surface. Caused by inadequate purge. Not repairable; the joint must be cut out.

**Lack of penetration or lack of fusion.** The joint looks complete from outside and is not fused through. Found by RT or UT, missed by visual and PT. Common in manual root passes.

**Sensitization.** Intergranular corrosion in the HAZ months or years later. Caused by carbon content plus the weld thermal cycle. Prevented by material selection.

**Weld toe fatigue cracking.** The joint fails in fatigue at the toe, where the geometric stress concentration and the residual tensile stress add. Not a strength failure and not predicted by a static check.

**Strain age cracking in 718.** Cracking during post-weld aging, driven by residual stress. Prevented by welding in the solution annealed condition.

**Titanium contamination.** Grey or white weld colour, irreversible embrittlement. Caused by inadequate shielding.

**Distortion pulling a joint out of alignment.** Discovered at final assembly, and by then the structure is welded.

**Arc strike outside the joint.** A momentary arc on the parent metal creates a tiny local quench zone that is a crack initiation site. It is a reject condition on flight hardware and is easy for a welder to dismiss as cosmetic.

---

## Operations

**Fit-up is most of the weld.** Square, burr-free, degreased tube ends with controlled gap. An orbital welder cannot fix bad fit-up and a manual welder should not have to.

**Clean before welding, not after.** Any hydrocarbon on the joint becomes carbon in the weld pool. Degrease and handle with clean gloves.

**Do not weld over a marker, a layout dye, or a temperature indicating crayon.** They contain chlorides and low-melting metals that cause cracking and corrosion.

**Record everything:** WPS number, welder ID, filler lot, gas lot, purge oxygen reading, heat input, date, and the inspection results. A weld with no record is a weld with no pedigree.

**Borescope internal welds** on anything with small passages or oxygen service. RT does not show the internal surface condition and that is what sheds particles.

**Leak test after welding and after any thermal cycle.** A weld that passes at ambient can open on the first cold cycle if there is a tight crack.

---

## Worked example

An orbital tube-to-fitting weld on the hydrazine feed line: 1/4 in OD x 0.028 in wall 316L, 3.5 MPa design pressure, 293 K, toxic fluid service, 500 pressure cycles over life, ER316L nominal chemistry.

| Quantity | Value |
|---|---|
| Joint efficiency E | 1.000 |
| Stress concentration K_t | 1.30 |
| Parent allowable | 113.33 MPa |
| HAZ yield (no knockdown, solid solution alloy) | 170.00 MPa |
| Weld allowable stress | 113.33 MPa |
| Total derating | 1.000 |
| Allowable pressure at 0.711 mm wall | 27.88 MPa |
| Design pressure | 3.50 MPa |
| **Pressure margin** | **7.97** |
| Hoop stress at MEOP | 12.13 MPa |
| Required wall for pressure | 0.097 mm |
| Chromium equivalent | 21.00 wt % |
| Nickel equivalent | 13.75 wt % |
| **Predicted ferrite number** | **5.3** |
| Required inspection | Radiography and penetrant |

The ferrite number of 5.3 is in the middle of the 3 to 10 window, so no cracking or embrittlement concern. The pressure margin of 8 is typical for small-bore tubing, where the wall is set by handling rather than by pressure. The toxic fluid classification drives the volumetric inspection requirement, which the tube-to-fitting geometry supports.

Contrast with a 6061-T6 socket weld, 1 in OD x 0.063 in wall, 2 MPa, oxidizer service:

| Quantity | Value |
|---|---|
| Joint efficiency E | 0.80 |
| HAZ yield factor | 0.55 |
| **Total derating** | **0.52** |
| Allowable pressure | 6.11 MPa |
| Pressure margin | 3.06 |
| Required inspection | Penetrant only, **flagged** |

Two flags come out: the joint carries only 52 percent of the parent metal allowable, and a socket weld in oxidizer service cannot be volumetrically inspected when the service requires it. The design action is to change the joint, not to accept the inspection limitation.

Reproduce with:

```python
from Weld import Weld

joint = Weld()
joint.setInputs({'jointType': 'tube to fitting', 'material': '316L',
                 'outerDiameter': 0.00635, 'wallThickness': 0.000711,
                 'designPressure': 3.5e6, 'designTemperature': 293.15,
                 'fluidHazard': 'toxic', 'pressureCycles': 500})

joint.calculateDerating()
joint.calculateAllowablePressure()
joint.calculateFerriteNumber()
joint.selectInspection()
print(joint.generateReport())
```

---

## Standards

| Standard | Scope |
|---|---|
| ASME BPVC Section IX | Welding, brazing and fusing qualifications |
| ASME B31.3 Chapter V | Fabrication, assembly and erection (piping welds) |
| AWS D17.1 | Fusion welding for aerospace applications |
| AWS D1.2 | Structural welding code, aluminum |
| AWS A5.9 | Bare stainless steel welding electrodes and rods |
| MSFC-SPEC-3679 | Process specification, welding, aerospace fluid systems hardware |
| NASA-STD-5006 | General welding requirements for aerospace materials |
| MIL-STD-1595 | Qualification of aircraft, missile and aerospace fusion welders |
| ANSI/AWS A4.2 | Calibration and measurement of ferrite content in austenitic weld metal |
| WRC Bulletin 342 | WRC-1992 constitution diagram for stainless steel weld metals |
| ASTM E1417 | Liquid penetrant testing |
| ASTM E1742 | Radiographic examination |
| ASTM E164 | Ultrasonic contact examination of weldments |

---

## Tool interface

The [`Weld`](../Weld.py) class covers derating, pressure capability, ferrite prediction and inspection selection.

```python
from Weld import Weld

joint = Weld()
joint.setInputs({'jointType': 'tube to fitting', 'material': '316L',
                 'outerDiameter': 0.00635, 'wallThickness': 0.000711,
                 'designPressure': 3.5e6, 'fluidHazard': 'toxic',
                 'pressureCycles': 500,
                 'chromium': 18.5, 'nickel': 12.0, 'molybdenum': 2.5,
                 'carbon': 0.02, 'nitrogen': 0.05})

joint.calculateDerating()           # E, HAZ knockdown, weld allowable stress
joint.calculateAllowablePressure()  # capability and margin at the actual wall
joint.calculateFerriteNumber()      # WRC-1992 prediction and window check
joint.selectInspection()            # required level from pressure and hazard
print(joint.generateReport())
```

Lookup tables: `Weld.WELD_JOINT_TYPES`, `Weld.HAZ_KNOCKDOWN`, `Weld.INSPECTION_LEVELS`.

---

## References

1. ASME BPVC Section IX, *Welding, Brazing, and Fusing Qualifications*.
2. AWS D17.1/D17.1M, *Specification for Fusion Welding for Aerospace Applications*.
3. Kotecki, D. J. and Siewert, T. A., "WRC-1992 Constitution Diagram for Stainless Steel Weld Metals", *Welding Journal*, Vol. 71, No. 5, 1992.
4. Lippold, J. C. and Kotecki, D. J., *Welding Metallurgy and Weldability of Stainless Steels*, Wiley, 2005.
5. MSFC-SPEC-3679, *Process Specification, Welding, Aerospace Fluid Systems Hardware*.
6. NASA-STD-5006B, *General Welding Requirements for Aerospace Materials*.
7. Messler, R. W., *Principles of Welding*, Wiley-VCH, 2004.
8. ASM Handbook Volume 6, *Welding, Brazing, and Soldering*, ASM International.
