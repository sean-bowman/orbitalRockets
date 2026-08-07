[Home](../../README.md) > Seals

# Seals

## Contents

- [Overview](#overview)
- [O-ring gland design](#o-ring-gland-design)
  - [Squeeze](#squeeze)
  - [Gland fill](#gland-fill)
  - [Stretch](#stretch)
  - [Extrusion and backup rings](#extrusion-and-backup-rings)
- [Material selection](#material-selection)
- [Temperature and the glass transition](#temperature-and-the-glass-transition)
- [Permeation](#permeation)
- [Compression set and stress relaxation](#compression-set-and-stress-relaxation)
- [Explosive decompression](#explosive-decompression)
- [Metal and spring-energized seals](#metal-and-spring-energized-seals)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Operations](#operations)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

An o-ring seal fails for one of four reasons, and the rubber is almost never among them:

1. The gland was the wrong size (too little squeeze, too much fill, too much stretch).
2. The extrusion gap was too large for the pressure.
3. The elastomer went glassy at temperature.
4. The material was not compatible with the fluid.

All four are design decisions made on a drawing, not manufacturing defects, and all four are checkable before anything is built.

The four numbers that define a gland are **squeeze**, **gland fill**, **stretch** and **extrusion gap**, and they conflict with one another. More squeeze improves sealing and raises fill. More fill removes the room the seal needs to expand thermally or swell in the fluid. More stretch thins the cross section and therefore reduces squeeze. Getting all four simultaneously into their windows is the whole job.

---

## O-ring gland design

### Squeeze

Squeeze is the compression of the cross section as a fraction of the free cross section diameter `W`:

```
squeeze = (W - groove depth) / W
```

The lower bound is set by sealing: below it, surface finish irregularities are not bridged and the seal leaks. The upper bound is set by compression set and gland fill: above it, the seal is permanently deformed and there is no room for expansion.

| Application | Squeeze range | Rationale |
|---|---|---|
| Static face seal (flange, boss) | 20 to 30 % | Highest, because there is no motion to generate friction or wear |
| Static radial (piston or rod groove) | 15 to 25 % | Lower, because installation over a shoulder limits it |
| Dynamic reciprocating | 10 to 20 % | Friction and wear scale with squeeze |
| Dynamic rotary | 8 to 15 % | Friction heating is the limit; a rotary o-ring can cook itself |
| High vacuum static | 25 to 30 % | Maximum squeeze minimizes the permeation cross section |

**Absolute squeeze matters as well as fractional squeeze.** A very small cross section (the AS568 `-0xx` series at 1.78 mm) at 20 percent squeeze is only 0.36 mm of absolute compression, which is not much more than the total tolerance stack of a typical gland. Small cross sections are therefore more sensitive to tolerances than large ones, and where possible the largest cross section that fits should be used.

### Gland fill

```
gland fill = A_oring / (groove depth x groove width)
```

| Fill | Consequence |
|---|---|
| < 60 % | The seal can roll, twist or spiral in the groove, particularly under a moving pressure differential |
| 60 to 90 % | The design window. Target 75 % |
| > 90 % | No room for thermal expansion or fluid swell |
| > 100 % | The groove hydraulically locks. The seal cannot be compressed further and the hardware yields or the seal extrudes |

The over-fill case is the dangerous one and it is easy to reach by accident, because elastomers have a coefficient of thermal expansion an order of magnitude higher than the metal around them and because many elastomers swell 5 to 20 percent in their service fluid. A gland designed at 85 percent fill at ambient, with a 10 percent volumetric swell, is at 94 percent. Add a temperature rise and it locks.

**Design at 75 percent nominal fill and check the worst case** with swell and thermal expansion included.

### Stretch

```
stretch = (groove ID - free o-ring ID) / free o-ring ID
```

| Limit | Value | Why |
|---|---|---|
| Installation maximum | 5 % | Above this the seal is damaged going on |
| Sustained maximum | 3 % | Above this, stress relaxation accelerates and the seal loses sealing force over time |

Stretch has a second, less obvious effect: **stretching the ring thins its cross section**, by roughly half the stretch percentage. A 4 percent stretch costs 2 percent of cross section, and that 2 percent comes directly out of the squeeze. A gland designed for 20 percent squeeze with a 4 percent stretched o-ring delivers about 18 percent. The [`Seal`](../Seal.py) class applies this correction.

For a face seal the opposite problem exists: an o-ring that is too large for the groove ID is **compressed circumferentially** rather than stretched, and it buckles out of the groove. Face seal grooves are sized so the ring is very slightly compressed, typically 1 to 3 percent, so it stays seated.

### Extrusion and backup rings

Under pressure the seal is forced into the clearance gap on the low-pressure side. If the gap is too large for the pressure and the durometer, the seal nibbles into it and eventually shears.

**Maximum diametral clearance before a backup ring is required** (Parker extrusion limits, inches):

| Pressure [psi] | 70 Shore A | 80 Shore A | 90 Shore A |
|---|---|---|---|
| 500 | 0.0115 | 0.0170 | 0.0230 |
| 1 000 | 0.0075 | 0.0120 | 0.0170 |
| 1 500 | 0.0055 | 0.0090 | 0.0130 |
| 2 000 | 0.0045 | 0.0075 | 0.0110 |
| 3 000 | 0.0030 | 0.0050 | 0.0085 |
| 5 000 | 0.0020 | 0.0035 | 0.0060 |

This is the check that catches the most common high-pressure seal failure: a gland that works perfectly on the bench at 500 psi and blows out at 3000 psi, because the clearance the machinist left is fine at the first and four times too large at the second.

**Three ways to fix an extrusion problem, in order of preference:**

1. **Reduce the clearance.** Tighter tolerance on the bore and the piston. Free, but it costs machining precision and can create an assembly problem.
2. **Harder durometer.** Going from 70 to 90 Shore A roughly doubles the allowable gap, at the cost of sealing compliance on a rough surface and of a higher required squeeze force.
3. **Backup ring.** A hard PTFE or PEEK anti-extrusion ring on the low-pressure side (or both sides for a bidirectional seal). Very effective, but it consumes groove width, so the gland must be designed for it from the start rather than added later.

**Use the worst-case clearance from the tolerance stack**, at the temperature where the differential thermal contraction is largest. On a cryogenic joint the aluminum bore shrinks more than the steel piston, and the gap at 77 K is larger than the gap at 293 K.

---

## Material selection

| Material | Temp range [K] | Tg [K] | He permeability | Key compatibility |
|---|---|---|---|---|
| FKM (Viton) | 253 to 477 | 255 | 12 | **Good:** N2O4, IRFNA, RP-1, GN2. **Bad:** hydrazine, MMH, ammonia, ketones |
| EPDM | 218 to 423 | 218 | 55 | **Good:** hydrazine, MMH, ammonia, water, steam. **Bad:** all hydrocarbons, LOX |
| NBR (Buna-N) | 233 to 393 | 233 | 20 | **Good:** RP-1, hydrocarbons, water. **Bad:** hydrazine, N2O4, LOX, ozone |
| VMQ (Silicone) | 218 to 505 | 213 | 300 | **Good:** dry heat, GN2. **Bad:** steam, oxidizers, high pressure gas |
| IIR (Butyl) | 218 to 393 | 208 | **5** | **Good:** hydrazine, MMH, gas retention. **Bad:** hydrocarbons |
| PTFE | 4 to 533 | none | 70 | Inert to essentially everything. Not an elastomer |
| PCTFE (Kel-F) | 4 to 423 | none | **3** | **The LOX-compatible choice.** Passes LOX mechanical impact |
| FFKM (Kalrez) | 258 to 600 | 264 | 10 | Nearly universal chemical compatibility. Very expensive |

*Permeability in units of 1e-8 scc-cm/(cm^2-s-atm) for helium at 298 K.*

**The three rules that matter most:**

1. **No NBR in hydrazine.** It degrades, and worse, it catalyzes decomposition of the propellant it is supposed to be containing. NBR is cheap and it is in every drawer, which is exactly why this mistake keeps happening. Use EPDM or butyl.
2. **No hydrocarbon-swelling elastomer in an oxidizer.** FKM in N2O4 is correct; EPDM in N2O4 is not.
3. **Nothing organic in LOX or GOX except PCTFE or PTFE**, and even those need to have passed LOX mechanical impact testing per NASA-STD-6001 Test 13 or ASTM G86 at the design pressure. See [MaterialsCompatibility.md](MaterialsCompatibility.md).

**A note on PTFE.** PTFE is chemically inert to essentially everything and usable to 4 K, which makes it look like the universal answer. It is not an elastomer. It cold flows under sustained load, it has essentially no elastic recovery, and it contracts 1.9 percent on cooling to LN2 against 0.3 percent for the stainless around it. A plain PTFE o-ring in a cryogenic joint loses all of its squeeze on the first cooldown and never gets it back. PTFE belongs in a spring-energized seal, where a metal spring supplies the recovery the polymer does not have.

---

## Temperature and the glass transition

This is the check people miss, and it is the one that produces the seal that "works fine in the lab and leaks on the pad".

An elastomer below its glass transition temperature `Tg` is not a soft seal. It is a hard plastic ring with the compliance of a washer. It cannot follow a joint that moves, it cannot accommodate a pressure change, and it will leak the instant anything shifts.

| Material | Tg | Practical consequence |
|---|---|---|
| FKM (Viton) | 255 K (-18 degC) | **Leaks on a cold morning.** Rules it out for anything cryogenic |
| NBR | 233 K (-40 degC) | Marginal for cold ambient |
| EPDM | 218 K (-55 degC) | The best of the common elastomers for cold |
| Butyl | 208 K (-65 degC) | Best cold capability of the common elastomers |
| Silicone | 213 K (-60 degC) | Good cold capability, but everything else about it is poor |

**Sealing force falls off steeply approaching Tg, not at Tg.** Carry at least 20 K of margin above the glass transition at the coldest excursion the seal will ever see, including a cold soak on the pad and a ground hold in winter.

**For genuinely cryogenic service** (below about 150 K) the options are:

- A metal seal (C-seal, K-seal, metal gasket)
- A spring-energized PTFE seal, where a stainless or Elgiloy spring provides the recovery
- PCTFE, heavily preloaded, accepting that it is a rigid seat rather than a compliant seal
- Indium or lead wire seals, for laboratory-scale joints

The **differential thermal contraction** must also be designed for. PTFE contracts 1.9 percent to 77 K and stainless contracts 0.30 percent. On a 20 mm gland that is a 0.32 mm differential, which is several times the squeeze on a small cross section. **Size the gland for the cold condition, not the ambient one.**

---

## Permeation

An elastomer is a semi-permeable membrane. Gas dissolves into the high-pressure face, diffuses through the material, and desorbs on the low-pressure face. This is not a leak through a hole, and no amount of squeeze reduces it.

```
Q = K * A * dP / t
```

with `K` the permeability coefficient, `A` the exposed sealing area, `dP` the differential and `t` the diffusion path (approximately the squeezed cross section).

**Permeation does not follow the molecular-mass scaling that a physical leak does**, because it is a solution-diffusion process rather than a flow. Relative to helium:

| Gas | Relative permeation rate |
|---|---|
| Hydrogen | 1.50 |
| Helium | 1.00 |
| CO2 | 1.20 |
| Oxygen | 0.35 |
| Methane | 0.25 |
| Nitrogen | 0.15 |
| Argon | 0.12 |

Hydrogen permeates faster than helium despite being heavier. Nitrogen permeates at 15 percent of the helium rate, which is one reason a helium leak check is conservative when the service gas is nitrogen.

**When permeation matters:**

- A short-duration system: never. Permeation is negligible against everything else.
- A spacecraft that must hold pressurant for years: often the **dominant** leak term.
- A GN2-pressurized system with elastomer seals over a decade: the pressurant loss is a real mission-level number.

This is the reason long-life spacecraft systems use metal seals or fully welded joints rather than o-rings, and it is a design decision that has to be made at architecture level rather than at the seal drawing.

---

## Compression set and stress relaxation

**Compression set** is the permanent deformation retained after a seal has been squeezed for a long time. It is measured per ASTM D395 as the fraction of the original deflection that is not recovered. An elastomer with 25 percent compression set that was installed at 20 percent squeeze has effectively 15 percent squeeze left.

Compression set accelerates with temperature (roughly doubling per 10 K in Arrhenius fashion), with squeeze, and with fluid exposure. A seal that will sit compressed at elevated temperature for years should be designed with squeeze at the high end of its window so there is something left at end of life.

**Stress relaxation** is the related phenomenon of sealing force decaying at fixed deflection. It is what actually determines whether the seal still seals. Both are why a seal has a shelf life and a service life, and why a system that has sat assembled for five years should be leak checked before it is trusted.

**Shelf life** for elastomer seals is set by SAE ARP5316 and by MIL-HDBK-695: typically 5 to 15 years depending on the polymer, from the cure date (not the purchase date), stored cool, dark, and uncompressed. Storing o-rings in a stretched or compressed condition destroys them.

---

## Explosive decompression

A seal held at high gas pressure for a long time absorbs gas into the polymer until it saturates. If the pressure is then released quickly, the dissolved gas comes out of solution inside the material faster than it can diffuse out, and the seal blisters, splits or fragments from the inside.

**Conditions that cause it:**

- High pressure (above roughly 7 MPa)
- A soluble gas (CO2 is the worst, helium and hydrogen also do it)
- Long saturation time
- Rapid depressurization

**Mitigations:**

- Depressurize slowly. A rate limit of a few MPa per minute is typical.
- Use a high-hardness, low free-volume compound. Explosive-decompression-resistant (ED or RGD) grades exist and are qualified per NORSOK M-710 or ISO 23936-2.
- Use a smaller cross section: the gradient is shallower and the gas escapes more easily.
- Use a metal seal.

This failure mode is well known in the oil and gas industry and less well known in aerospace, where it shows up in high-pressure helium systems that are cycled.

---

## Metal and spring-energized seals

Where an elastomer will not work -- cryogenic temperature, extreme temperature, hard vacuum, long-duration permeation limits, radiation, or extreme chemical exposure -- the alternatives are:

| Type | Mechanism | Leak class | Notes |
|---|---|---|---|
| **C-seal** | C-section metal ring, pressure energized | 1e-8 scc/s | The open side faces the pressure so internal pressure increases the sealing force. Requires a defined groove and controlled compression |
| **E-seal / O-seal** | Thin-wall metal ring acting as a spring | 1e-8 scc/s | Higher springback than a C-seal, more forgiving of flange deflection |
| **K-seal / omega seal** | Pressure-energized metal seal | 1e-9 scc/s | Very high pressure and temperature capability |
| **Spring-energized PTFE (Bal Seal, Variseal)** | PTFE or filled-PTFE jacket over a metal spring | 1e-6 scc/s | The standard cryogenic dynamic seal. The spring supplies the recovery PTFE lacks |
| **Metal gasket (VCR, ConFlat)** | Soft metal yielded between hard surfaces | 1e-9 to 1e-11 scc/s | Consumed on each make-up |
| **Plated metal seals** | Silver or gold plating over an Inconel core | 1e-9 scc/s | The plating conforms to asperities; the core provides springback. Note silver is not LOX compatible |

**Design considerations for metal seals:**

- **Surface finish is everything.** Typically 16 to 32 microinch Ra on the sealing faces, and the lay must be circumferential rather than radial. A radial machining mark is a leak path straight across the seal.
- **Compression must be controlled.** Metal seals work in a narrow band of compression: too little and the asperities are not filled, too much and the seal is crushed flat and loses springback. Groove depth tolerance is tight.
- **Seating load is high.** An order of magnitude above an elastomer. The flange and bolting have to deliver it without deflecting enough to open the joint at the far side.
- **Single use in most cases.** A metal seal that has been compressed has yielded, and it does not come back.

---

## Design rules of thumb

| Rule | Value | Why |
|---|---|---|
| Static face squeeze | 20 to 30 %, target 25 % | Sealing at the bottom, compression set at the top |
| Gland fill | 60 to 90 %, target 75 % | Rolling below, hydraulic lock above |
| Installed stretch | < 3 % sustained, < 5 % install | Stress relaxation and cross section thinning |
| Cross section loss from stretch | About half the stretch percent | Comes directly out of the squeeze |
| Glass transition margin | > 20 K above Tg at the coldest excursion | Sealing force falls off before Tg is reached |
| Design point for cryogenic glands | The cold condition | Differential contraction removes squeeze |
| Extrusion gap | Worst-case tolerance stack, at the worst temperature | Nominal clearance is not the design case |
| Depressurization rate at high pressure | A few MPa/min | Explosive decompression |
| Prefer the largest cross section that fits | Always | Absolute squeeze scales with W; tolerance sensitivity does not |
| Elastomer shelf life | 5 to 15 years from cure date | ARP5316; store cool, dark, uncompressed |
| Surface finish for elastomer seal | 32 microinch Ra or better | Below this the seal cannot bridge the asperities |
| Surface finish for metal seal | 16 to 32 microinch Ra, circumferential lay | A radial mark is a leak path |

---

## Failure modes

**Extrusion / nibbling.** Chunks missing from the low-pressure side. Caused by too large a clearance for the pressure. Fix with clearance, durometer or a backup ring.

**Compression set.** The seal is flat-sided and does not recover. Caused by time, temperature and excessive squeeze. Predictable and designable.

**Spiral failure.** The seal is twisted and cut in a helical pattern. Caused by a dynamic seal rolling rather than sliding in its groove, usually because gland fill is too low or friction is too high.

**Glass transition leakage.** The seal looks perfect and leaks cold. Caused by material selection. The seal will pass every ambient leak check.

**Chemical attack.** Swelling, softening, hardening, cracking or dissolution. Caused by material selection. In hydrazine with NBR it goes further: the seal catalyzes propellant decomposition, which means the seal failure and a pressure excursion arrive together.

**Explosive decompression.** Internal blisters and splits after a rapid depressurization from high gas pressure.

**Installation damage.** A cut, nicked or twisted seal from installation over a sharp edge or thread. Every gland should have a lead-in chamfer, and threads that the seal passes over should be taped or covered during assembly.

**Over-fill hydraulic lock.** The seal cannot be compressed and the hardware yields, or the seal extrudes catastrophically. Caused by a fill calculation that omitted thermal expansion or fluid swell.

**Contamination trapped under the seal.** A single hair or particle across the sealing land is a leak path that no torque closes.

---

## Operations

**Inspect every seal before installation.** Under magnification, for nicks, flash, mold defects and contamination. A seal costs almost nothing; finding a bad one after assembly costs a rebuild.

**Lubricate for installation, sparingly, with a compatible fluid.** A trace of the service fluid, or a compatible grease. Never a hydrocarbon grease in an oxidizer system.

**Never reuse a seal that has been compressed** unless the design explicitly permits it and the compression set has been characterized.

**Control by part number, not by dimension.** Two o-rings of the same size in different materials are indistinguishable by eye and one of them will destroy the system.

**Record cure date and installation date.** Shelf life runs from cure date, and service life runs from installation.

**Store correctly.** Cool, dark, sealed, uncompressed and unstretched. UV and ozone attack elastomers in storage, and a bag of o-rings left on a windowsill is scrap.

---

## Worked example

A static face seal on a hydrazine flange: AS568 `-0xx` series (1.78 mm cross section), 12.0 mm free inner diameter, EPDM at 70 Shore A, groove ID 12.4 mm, 2.5 MPa sealed differential, 293 K nominal with a 273 K cold excursion, 0.15 mm diametral clearance.

**Compatibility:** EPDM is on the verified hydrazine-compatible list. Tg is 218 K against a 273 K cold excursion, a 55 K margin, which clears the 20 K rule.

**Gland sizing:**

| Quantity | Value |
|---|---|
| Installed stretch | 3.33 % |
| Effective cross section after stretch | 1.749 mm |
| Groove depth | 1.311 mm |
| Groove width | 2.441 mm |
| Achieved squeeze | 24.58 % (0.437 mm) |
| Gland fill | 75.0 % |

The stretch flags a caution: 3.33 percent exceeds the 3 percent sustained limit. It is acceptable for assembly but will accelerate stress relaxation, and the correct fix is to select the next larger o-ring inner diameter.

**Extrusion:** At 2.5 MPa (363 psi) and 70 durometer the allowable diametral gap is 0.292 mm against an actual 0.150 mm. No backup ring required, with a factor of two of margin.

**Permeation:** 2.94e-5 scc/s of helium, which is 0.93 standard litres per year. For a launch vehicle that is irrelevant. For a ten-year spacecraft holding pressurant it is 9 litres, which is a number that has to go into the pressurant budget.

Reproduce with:

```python
from Seal import Seal

flangeSeal = Seal()
flangeSeal.setInputs({'sealType': 'static face', 'material': 'epdm',
                      'crossSectionDiameter': 0.070 * 0.0254, 'innerDiameter': 0.012,
                      'grooveInnerDiameter': 0.0124, 'durometer': 70,
                      'designPressure': 2.5e6, 'designTemperature': 293.15,
                      'minimumTemperature': 273.0, 'fluid': 'N2H4',
                      'diametralClearance': 0.00015})
flangeSeal.checkCompatibility()
flangeSeal.sizeGland()
flangeSeal.checkExtrusion()
flangeSeal.calculatePermeation('He')
print(flangeSeal.generateReport())
```

---

## Standards

| Standard | Scope |
|---|---|
| SAE AS568 | Aerospace size standard for o-rings |
| SAE AS4716 | Gland design, o-ring and other elastomeric seals, static radial |
| SAE AS5857 | Gland design, o-rings and other elastomeric seals, static face |
| SAE ARP1232 | Gland design, elastomeric o-ring seals, dynamic radial |
| SAE ARP5316 | Storage of elastomer seals and seal assemblies |
| ASTM D395 | Rubber property, compression set |
| ASTM D1414 | Rubber o-rings, test methods |
| ASTM D2000 | Rubber products in automotive applications (classification system) |
| MIL-P-25732 | Packing, preformed, petroleum hydraulic fluid resistant |
| MIL-DTL-83248 | Packing, preformed, fluorocarbon rubber (Viton) |
| NASA-STD-6001 Test 13 | Mechanical impact of materials in variable pressure LOX and GOX |
| ASTM G86 | Determining ignition sensitivity of materials to mechanical impact in oxygen |
| ISO 23936-2 / NORSOK M-710 | Elastomer qualification including rapid gas decompression |

---

## Tool interface

The [`Seal`](../Seal.py) class covers gland sizing, extrusion, compatibility and permeation.

```python
from Seal import Seal

seal = Seal()
seal.setInputs({'sealType': 'static face', 'material': 'epdm',
                'crossSectionDiameter': 0.00178, 'innerDiameter': 0.012,
                'grooveInnerDiameter': 0.0124, 'durometer': 70,
                'designPressure': 2.5e6, 'minimumTemperature': 273.0,
                'fluid': 'N2H4', 'diametralClearance': 0.00015})

seal.checkCompatibility()    # raises CompatibilityError on fluid, temperature or Tg violation
seal.sizeGland()             # groove depth and width, squeeze, fill, stretch
seal.checkExtrusion()        # backup ring requirement
seal.calculatePermeation('He')
print(seal.generateReport())
```

Lookup tables: `Seal.SEAL_MATERIALS`, `Seal.SQUEEZE_RANGES`, `Seal.EXTRUSION_GAP_IN`, `Seal.AS568_CROSS_SECTIONS_IN`, `Seal.PERMEATION_SPECIES_FACTOR`.

---

## References

1. Parker Hannifin, *Parker O-Ring Handbook*, ORD 5700.
2. SAE AS5857, *Gland Design, O-Rings and Other Elastomeric Seals, Static Face Type*.
3. SAE AS4716, *Gland Design, O-Ring and Other Elastomeric Seals, Static Radial*.
4. SAE ARP5316, *Storage of Elastomer Seals and Seal Assemblies Which Include an Elastomer Element*.
5. Barron, R. F., *Cryogenic Systems*, 2nd ed., Oxford University Press, 1985.
6. Flitney, R. K., *Seals and Sealing Handbook*, 6th ed., Elsevier, 2014.
7. NASA-STD-6001B, *Flammability, Offgassing, and Compatibility Requirements and Test Procedures*.
8. Bauer, P., Glickman, M. and Iwatsuki, F., *Analytical Techniques for the Design of Seals for Use in Rocket Propulsion Systems*, AFRPL-TR-65-61, 1965.
