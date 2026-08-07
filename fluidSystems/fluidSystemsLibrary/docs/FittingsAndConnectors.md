[Home](../../README.md) > Fittings and Connectors

# Fittings and Connectors

## Contents

- [Overview](#overview)
- [Fitting families](#fitting-families)
- [Selection](#selection)
- [Sealing mechanisms](#sealing-mechanisms)
- [Preload, torque and the nut factor](#preload-torque-and-the-nut-factor)
- [Pressure loss](#pressure-loss)
- [Galling and thread damage](#galling-and-thread-damage)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Operations](#operations)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Every fitting is a leak path. That is the governing fact and it should drive the design: the cheapest, lightest and most reliable joint is the one that is not there.

The design sequence follows from that:

1. **Weld it** if the joint is permanent. Lowest leak rate, lowest mass, lowest pressure drop, no torque to control, no seal to age. See [Welds.md](Welds.md).
2. **Use a mechanical fitting** only where the system genuinely has to come apart -- for assembly access, for component replacement, for a ground umbilical interface, or because a component ships with threaded ports and cannot be welded.
3. **Minimize the count.** Every union added is a leak path added, an inspection added, a torque record added and a mass increment added.

When a mechanical joint is required, the selection is a trade among five properties, and they conflict:

| Property | Why it matters |
|---|---|
| Pressure and temperature capability | Obvious, and rarely the binding constraint on small bore |
| Achievable leak class | Spans six orders of magnitude across families. Usually the binding constraint |
| Reusability | How many make-and-break cycles before the sealing surface is spent |
| Cleanliness compatibility | Whether the joint can be cleaned, and whether it generates debris |
| Mass and envelope | Fitting mass on a small-bore vehicle run is comparable to tube mass |

---

## Fitting families

| Family | Standard | Rating (1/4 in) | Temp range [K] | Leak class [scc/s He] | Reuse | K |
|---|---|---|---|---|---|---|
| AN/MS 37 deg flare | AS4395 / MS33656 / AN818 | 20.7 MPa | 20 to 700 | 1e-4 | 25 | 0.20 |
| Flareless (bite) | MS21902 / AS5852 | 20.7 MPa | 77 to 550 | 1e-4 | 10 | 0.25 |
| Compression (two-ferrule) | Swagelok / CPI / Gyrolok | 40.0 MPa | 4 to 800 | 1e-6 | 25 | 0.25 |
| VCR metal gasket | Swagelok VCR | 34.5 MPa | 4 to 920 | 4e-9 | 100 | 0.15 |
| VCO o-ring face seal | Swagelok VCO | 20.7 MPa | 220 to 500 | 1e-7 | 50 | 0.18 |
| SAE straight thread boss | SAE J1926 / MS16142 / AS5202 | 34.5 MPa | 220 to 450 | 1e-6 | 25 | 0.30 |
| NPT tapered pipe thread | ASME B1.20.1 | 10.0 MPa | 220 to 550 | 1e-3 | 3 | 0.35 |
| Grayloc / Destec clamp hub | proprietary | 100 MPa | 20 to 900 | 1e-8 | 100 | 0.10 |
| ConFlat knife edge | ISO 3669 / ASTM F1836 | 1.0 MPa | 4 to 720 | 1e-10 | 100 | 0.12 |
| Raised face flange | ASME B16.5 | 10.0 MPa | 220 to 800 | 1e-4 | 50 | 0.08 |
| Quick disconnect | MIL-C-25427, vendor | 20.7 MPa | 20 to 400 | 1e-4 | 500 | 2.00 |

**AN/MS 37 degree flare.** The aerospace workhorse. The tube end is flared to a 37 degree cone and clamped between the fitting nose and a sleeve by the nut. Metal-to-metal sealing, no elastomer, no consumable, cryogenic capable, inspectable and reusable. The failure mode is the flare: a cracked, eccentric, over-thinned or under-formed flare is by a large margin the most common leak source in any aerospace fluid system. Note the 37 degree angle carefully. **45 degree SAE flare fittings look identical and will not seal against a 37 degree flare.** Mixing them is a recurring and entirely avoidable failure.

**Compression (two-ferrule).** A front and back ferrule swage onto the tube OD as the nut is tightened. Outstanding leak tightness and pressure capability with no tube-end forming operation. Critically, ferrules and bodies from different manufacturers **do not interchange** even when they appear identical, and mixing them is a documented failure mode. Compression fittings are specified by **turns past finger tight**, not by torque: 1-1/4 turns on initial make-up, and much less on remake. A torque wrench on a Swagelok fitting is the wrong tool.

**VCR metal gasket face seal.** Two beads face each other with a replaceable metal gasket between them, captured in a retainer. The best readily available leak tightness in a demountable joint, about 4e-9 scc/s. The gasket is consumed on every make-up, which is a feature rather than a drawback: the sealing surface is renewed every time, so the joint does not degrade with cycles the way an o-ring or a flare does. The standard for ultra-high-purity gas, high vacuum and anywhere external leakage genuinely matters.

**SAE straight thread boss.** A straight (not tapered) thread carries the load and an o-ring in a chamfered boss face does the sealing. Because the two functions are separated, the joint is repeatable in a way that NPT is not: the thread is torqued to a defined value, the o-ring seals independently, and the joint can be oriented (for an elbow) and locked with a jam nut.

**NPT tapered pipe thread.** Seals by interference between tapered threads plus tape or paste. Almost everything about it is wrong for a flight system: it is not repeatable, it generates thread debris on every make-up, the sealant is a contamination source and a compatibility problem, the achievable leak rate is poor, and the joint is under a wedging stress that can split a thin-wall boss. It is acceptable on a ground test stand and nowhere else. **Never use NPT in an oxygen system or with a hazardous fluid.**

**Grayloc and similar clamp hubs.** A metal seal ring sits between two hubs held by a clamp. The seal is pressure energized: higher internal pressure pushes the ring lips harder against the hubs, so the seal gets tighter as the load increases. Very high pressure capability in a compact, quickly-demountable package. The standard for large-bore high-pressure test stand plumbing.

**Quick disconnects.** Every ground umbilical interface. High pressure loss and a much worse leak class than a made-up joint, in exchange for operability. The number that has to be verified is the **separation force at pressure**: a QD that will not separate under residual pressure is a launch hold, and one that separates too easily is a hazard.

---

## Selection

| Requirement | Choose | Why |
|---|---|---|
| Permanent joint | Weld | Best on every axis except serviceability |
| General aerospace tubing, reusable | AN/MS flare | Proven, inspectable, cryogenic capable |
| Best demountable leak tightness | VCR | 4e-9 scc/s, gasket renewed each make-up |
| Very high pressure, small bore | Compression | 40 MPa in 1/4 in |
| Very high pressure, large bore | Grayloc | Pressure energized metal seal |
| Component port interface | SAE boss | Repeatable, orientable, standard on valve bodies |
| Ground umbilical | Quick disconnect | The only option that operates |
| Ultra high vacuum | ConFlat | 1e-10 scc/s, but low internal pressure capability |
| Ground test stand, non-hazardous | NPT is acceptable | Cheap, fast, and nothing else about it recommends it |
| Cryogenic | AN flare, compression, VCR, Grayloc | Metal-to-metal sealing. **Not** anything relying on an elastomer |
| Hazardous fluid | VCR or welded | The leak class requirement usually rules everything else out |

**A note on temperature.** The lower limit in the family table is set by the sealing element, and for every elastomer-sealed family (VCO, SAE boss) it is the glass transition of the o-ring, not the metal. Below Tg an elastomer has no compliance and the joint leaks the instant it moves. See [Seals.md](Seals.md).

**A note on size derating.** Fitting pressure ratings fall with size roughly as `1/d`, because the end load rises as `d^2` while the thread area rises as `d`. A family rated 20.7 MPa at 1/4 inch is not rated 20.7 MPa at 1 inch. The [`Fitting`](../Fitting.py) class applies a `1/d` derate from a 1/4 inch reference; vendor catalog values supersede it.

---

## Sealing mechanisms

Four mechanisms, in rough order of achievable leak tightness:

**1. Elastic metal-to-metal (flare, cone).** Two machined metal surfaces are elastically deformed against each other. Requires enough preload to yield the surface asperities but not so much as to crack the flare. Achievable leak rate 1e-4 to 1e-5 scc/s, limited by the surface finish and by the fact that the sealing land is comparatively wide.

**2. Plastic deformation of a soft gasket (VCR, ConFlat, Grayloc).** A softer element (nickel or copper gasket, or a metal seal ring) is deliberately yielded into the harder sealing surfaces, conforming to every asperity. Achievable leak rate 1e-8 to 1e-11 scc/s. The gasket is consumed.

**3. Elastomer compression (o-ring face seal, SAE boss).** An elastomer is squeezed into the sealing gap. Excellent leak tightness for a molecular-flow leak, but limited by **permeation** through the elastomer itself, which no amount of squeeze reduces. Achievable 1e-6 to 1e-7 scc/s.

**4. Thread interference plus sealant (NPT).** The threads gall together and a sealant fills the helical leak path. Achievable 1e-3 scc/s at best, and highly variable.

**Pressure energization** is a fifth idea layered onto the others. A seal geometry that lets internal pressure act to increase the sealing force (a C-seal, a Grayloc ring, a lip seal) gets tighter as the load increases rather than looser. That is the right architecture for a joint that must hold a wide pressure range, and it is the opposite of a plain compressed gasket, whose sealing force is fixed at assembly and is progressively overcome by the pressure end load.

---

## Preload, torque and the nut factor

Torque is a proxy for preload, and it is a poor one.

```
T = K * F * d
```

with `K` the nut factor, `F` the preload and `d` the nominal thread diameter. The problem is that `K` is not a constant. It lumps together the thread friction, the bearing face friction and the thread helix contribution, and the friction terms account for 85 to 90 percent of the applied torque. **Only 10 to 15 percent of the torque you apply becomes preload.** Anything that changes friction changes preload proportionally.

| Condition | Nut factor K | Preload relative to dry |
|---|---|---|
| Dry stainless on stainless | 0.25 to 0.35 | 1.0 (and prone to galling) |
| Silver plated | 0.18 to 0.22 | 1.4 |
| Cadmium plated | 0.16 to 0.20 | 1.6 |
| PTFE coated / Krytox | 0.12 to 0.16 | 2.0 |
| Molybdenum disulfide | 0.11 to 0.14 | 2.3 |

Applying the same torque to a dry joint and a lubricated joint produces preloads that differ by more than a factor of two. That is why torque specifications must state the lubrication condition, and why "clean and dry" on a drawing is a torque-relevant instruction rather than a cleanliness note.

**Better methods than torque, where preload actually matters:**

1. **Turns past finger tight (FFFT).** Controls the axial displacement directly, and displacement times joint stiffness is preload. Immune to friction variation. This is how compression fittings are specified and it is the right method for any joint where the geometry is repeatable.
2. **Bolt stretch measurement.** Ultrasonic or micrometer measurement of bolt elongation. The most accurate method, used on large flanges and critical structural joints.
3. **Torque plus angle.** Snug to a low torque to seat the joint, then rotate a specified angle. Combines the two.
4. **Tabulated torque from the standard.** For AN/MS flare fittings, use **MS33566** and its derivatives. The standard specifies torque directly because the flare geometry, not the preload, sets the sealing stress, and the tabulated value is calibrated to produce it. Do not compute a preload for a flare fitting.

**MS33566 flare fitting torque** (steel and stainless tube, in-lbf):

| Dash | Tube OD | Torque range |
|---|---|---|
| -2 | 1/8 in | 20 to 30 |
| -3 | 3/16 in | 30 to 40 |
| -4 | 1/4 in | 40 to 65 |
| -5 | 5/16 in | 60 to 80 |
| -6 | 3/8 in | 75 to 125 |
| -8 | 1/2 in | 150 to 250 |
| -10 | 5/8 in | 200 to 350 |
| -12 | 3/4 in | 300 to 500 |
| -16 | 1 in | 500 to 700 |
| -20 | 1-1/4 in | 700 to 900 |
| -24 | 1-1/2 in | 800 to 1000 |

Aluminum tube values are lower. **Over-torquing a flare fitting cracks the flare**, and the crack is often invisible until the joint is pressurized and cycled. It is the single most common cause of an AN fitting leak, and it comes from a technician who could not get a joint to stop weeping and kept tightening. The correct response to a weeping flare joint is to disassemble and inspect the flare, not to add torque.

---

## Pressure loss

```
dP = K * rho * V^2 / 2
```

referenced to the tube inner diameter. Individual fittings are small; collectively they are not. A vehicle run with a dozen unions, two elbows and a quick disconnect can easily carry more loss than the straight tube it connects, and it is the term most often omitted from a first-pass pressure budget.

The quick disconnect entry (`K = 2.0`) deserves attention. A QD is two poppets, two flow reversals and a restricted annulus. Its loss is highly design dependent and the catalog `Cv` is often optimistic. Measure the one you are using.

---

## Galling and thread damage

Austenitic stainless steel galls against austenitic stainless steel. The oxide film that makes the alloy corrosion resistant is thin and it is wiped off by sliding contact, exposing clean metal that cold-welds to the mating surface. Once galling starts, the joint seizes and the only way out is destructive.

**Mitigations, in order of preference:**

1. **Dissimilar hardness.** A 316 nut on a 17-4 PH body, or a nut with a different work-hardening history. Different hardness prevents the cold weld.
2. **Silver plating.** Standard on aerospace flare nuts. Silver is soft, has a low shear strength, and shears rather than welding. It also reduces the nut factor, which improves preload repeatability. **Silver is not acceptable in liquid oxygen** (it is a decomposition catalyst for some propellants and has oxygen compatibility limits), so check the fluid.
3. **Anti-seize compound.** Effective, but every anti-seize is a contaminant and a compatibility question. Nickel-based and copper-based compounds are common; **copper-based is unacceptable in hydrazine** because copper catalyzes its decomposition. In oxygen service, only approved perfluorinated products.
4. **Slow, steady tightening.** Galling is aggravated by high sliding speed. Run the nut down by hand and torque slowly.

---

## Design rules of thumb

| Rule | Value | Why |
|---|---|---|
| Minimize joint count | Fewest possible | Every joint is a leak path, an inspection and a mass increment |
| Weld unless it must come apart | Always | Best leak rate, mass, pressure drop |
| Flare angle | 37 degrees for AN/MS, 45 for SAE | They look identical and do not interchange |
| Compression fitting make-up | 1-1/4 turns past finger tight | Not torque specified |
| Never mix ferrule brands | Absolute | Documented failure mode |
| Torque that becomes preload | 10 to 15 % | The rest is friction |
| Lubricated vs dry preload | 2x at the same torque | Specify lubrication with torque |
| Pressure rating size derate | Roughly `1/d` from 1/4 in | End load rises as `d^2` |
| Fitting leak contribution | Sum over all joints | Leak rates add |
| Access | Every joint reachable with its tool and its leak check probe | Retrofitting access is expensive |
| Wrench flats | Always provide a backup wrench flat | Torquing against the tube twists and cracks it |

---

## Failure modes

**Cracked flare.** The dominant AN fitting failure. Caused by over-torque, by a flaring tool that thinned the flare, by re-flaring an already-worked tube end, or by repeated make-and-break. Inspect the flare with magnification on every disassembly and re-flare rather than reusing a marginal one.

**Ferrule mismatch.** Ferrules from vendor A in a body from vendor B. Looks assembled, holds pressure on the bench, leaks in service or blows out. Enforce single-source ferrules and bodies.

**Over-torque splitting a boss.** An NPT fitting wedges as it is tightened and can split a thin-walled port boss. The crack is often not visible until the part is proof tested.

**Galled and seized threads.** Covered above. The failure is discovered during disassembly, which is usually the worst possible time.

**Loosening under vibration.** A fitting that is not lock-wired, not staked and not preloaded adequately backs off. Every threaded joint in a vibration environment needs a positive retention feature or verified adequate preload.

**Elastomer seal failure at temperature.** A VCO or SAE boss joint that works at room temperature leaks on a cold morning because the o-ring passed its glass transition. See [Seals.md](Seals.md).

**Contamination generated by assembly.** Thread sealant, PTFE tape shreds, galling debris and flaring chips all end up downstream. PTFE tape in particular is a known source of orifice plugging and valve seat damage; it should not be used in a system with small passages, and never in oxygen service.

**Wrong sealing element reinstalled.** A VCR gasket reused, an o-ring of the wrong material fitted because it was the right size. Control seal material at the part number level, not the dimension level.

---

## Operations

**Torque records.** Record the applied torque, the tool used, its calibration date, and the lubrication condition for every flight joint. When a leak appears later, the torque record is the first thing anyone asks for.

**Backup wrench.** Always. Torquing a nut against an unrestrained tube twists the tube, cracks the flare and misaligns the joint.

**Leak check every joint after every make-up.** A joint that was fine last time is not evidence about this time. Use the method appropriate to the required leak class; see [Leaks.md](Leaks.md).

**Cap everything.** An open tube end collects debris in minutes. Cap on disassembly and do not remove the cap until the moment of assembly.

**Cleanliness at assembly.** The joint interior is exposed exactly once, at assembly. Anything on the sealing surfaces at that moment is inside the system forever. Clean gloves, clean tools, clean bench, no compressed shop air.

**Do not reuse a consumed element.** VCR gaskets, ConFlat copper gaskets, crush washers and bite-type ferrules are single use. Reusing one is a guaranteed leak and it is a common shortcut under schedule pressure.

---

## Worked example

Two AN/MS 37 degree flare unions on a 1/4 in OD x 0.028 in wall hydrazine line, 0.045 kg/s, 3.5 MPa design pressure, 293 K, 316L body.

| Quantity | Value |
|---|---|
| Dash size | -4 |
| Pressure rating (derated) | 20.7 MPa |
| Pressure margin | 5.91 |
| Reuse cycles | 25 |
| Leak class per joint | 1e-4 scc/s He |
| Aggregate leak, two joints | 2e-4 scc/s He |
| Total K | 0.400 |
| Velocity | 2.34 m/s |
| Pressure loss | 1.10 kPa |
| Installation torque | 4.52 to 7.34 N-m (40 to 65 in-lbf) |

Two flags come out of the selection screening:

- 1e-4 scc/s per joint is **loose for hydrazine service**. If the system-level allowable is 1e-6 scc/s, two flare joints alone blow the budget by two orders of magnitude and the joint must be VCR or welded.
- Austenitic stainless threads gall. Silver-plated nuts or an approved anti-seize (not copper-based, which catalyzes hydrazine decomposition).

Reproduce with:

```python
from Fitting import Fitting

union = Fitting()
union.setInputs({'fittingType': 'an flare', 'tubeOuterDiameter': 0.00635,
                 'tubeInnerDiameter': 0.004928, 'quantity': 2, 'fluid': 'N2H4',
                 'designPressure': 3.5e6, 'designTemperature': 293.15,
                 'massFlow': 0.045, 'density': 1008.5})
union.checkCompatibility()
union.calculatePressureLoss()
union.calculateTorque()
print(union.generateReport())
print(union.compareTypes(['an flare', 'compression', 'vcr', 'npt', 'sae boss', 'grayloc']))
```

The comparison table is the useful output for a selection decision:

| Type | Rating [MPa] | Temp [K] | Leak [scc/s] | Reuse | K | Status |
|---|---|---|---|---|---|---|
| an flare | 20.7 | 20-700 | 1e-04 | 25 | 0.20 | CAUTION |
| compression | 40.0 | 4-800 | 1e-06 | 25 | 0.25 | OK |
| vcr | 34.5 | 4-920 | 4e-09 | 100 | 0.15 | OK |
| npt | 10.0 | 220-550 | 1e-03 | 3 | 0.35 | CAUTION |
| sae boss | 34.5 | 220-450 | 1e-06 | 25 | 0.30 | OK |
| grayloc | 100.0 | 20-900 | 1e-08 | 100 | 0.10 | OK |

---

## Standards

| Standard | Scope |
|---|---|
| SAE AS4395 | Fitting end, standard dimensions for flared tube connection, 37 degree |
| SAE AS5202 | Port and fitting end, internal straight thread |
| MS33656 | Fitting end, standard dimensions for flared tube connection |
| MS33566 | Fitting installation, flared tube, torque values |
| AN818 | Nut, tube coupling |
| MS21902 | Fitting, flareless tube |
| SAE J1926 | Connections for general use and fluid power, ports and stud ends |
| ASME B1.20.1 | Pipe threads, general purpose (inch) |
| ASME B16.5 | Pipe flanges and flanged fittings |
| ISO 3669 | Vacuum technology, dimensions of knife-edge flanges |
| MIL-C-25427 | Coupling, quick disconnect |
| NASA-STD-8739.4 | Crimping, interconnecting cables, harnesses and wiring (referenced for workmanship practice) |
| ASTM G88 | Designing systems for oxygen service |
| SAE ARP1176 | Oxygen system and component cleaning and packaging |

---

## Tool interface

The [`Fitting`](../Fitting.py) class covers selection screening, pressure loss and torque.

```python
from Fitting import Fitting

union = Fitting()
union.setInputs({'fittingType': 'vcr', 'tubeOuterDiameter': 0.00635,
                 'tubeInnerDiameter': 0.004928, 'quantity': 4,
                 'fluid': 'N2H4', 'designPressure': 3.5e6,
                 'designTemperature': 293.15, 'massFlow': 0.045, 'density': 1008.5})

union.checkCompatibility()      # raises CompatibilityError on a hard stop
union.calculatePressureLoss()   # K, velocity, dP, aggregate leak
union.calculateTorque()         # MS33566 table for flare, preload estimate otherwise
print(union.compareTypes())     # full selection matrix at these conditions
```

Lookup tables: `Fitting.FITTING_TYPES`, `Fitting.AN_FLARE_TORQUE_INLBF`, `Fitting.INCOMPATIBLE_COMBINATIONS`.

---

## References

1. SAE AS4395, *Fitting End, Standard Dimensions for Flared Tube Connection and Gasket Seal*.
2. MS33566, *Fitting Installation, Flared Tube, Torque Values*.
3. FAA AC 43.13-1B, *Acceptable Methods, Techniques, and Practices -- Aircraft Inspection and Repair*, Chapter 9 (fluid lines and fittings).
4. Swagelok, *Tube Fitter's Manual*, MS-CRD-TFM.
5. Bickford, J. H., *An Introduction to the Design and Behavior of Bolted Joints*, 4th ed., CRC Press, 2007.
6. NASA-STD-5020, *Requirements for Threaded Fastening Systems in Spaceflight Hardware*.
7. ASTM G88-13, *Standard Guide for Designing Systems for Oxygen Service*.
8. Huzel, D. K. and Huang, D. H., *Modern Engineering for Design of Liquid-Propellant Rocket Engines*, AIAA, 1992.
