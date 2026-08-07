[Home](../../README.md) > Cleanliness and Contamination

# Cleanliness and Contamination

## Contents

- [Overview](#overview)
- [Cleanliness levels](#cleanliness-levels)
- [Where contamination comes from](#where-contamination-comes-from)
- [Cleaning processes](#cleaning-processes)
- [Oxygen cleaning](#oxygen-cleaning)
- [Verification](#verification)
- [Maintaining cleanliness](#maintaining-cleanliness)
- [Design for cleanability](#design-for-cleanability)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Contamination causes three distinct kinds of failure and the mitigations are different for each:

| Type | Failure | Mitigation |
|---|---|---|
| **Particulate** | Plugs orifices, damages valve seats, abrades catalyst | Filtration and cleaning |
| **Non-volatile residue (NVR)** | Ignition source in oxygen; catalyst poison; seal degradation | Solvent cleaning and verification |
| **Moisture** | Ice, corrosion, catalyst poison, acid formation in N2O4 | Drying and purge |

The governing principle is that **you cannot clean an assembled system properly.** Cleaning happens at the part level, before assembly, and everything after that is about not re-contaminating it.

---

## Cleanliness levels

**IEST-STD-CC1246** (formerly MIL-STD-1246) defines particulate cleanliness levels. The level number is the size in microns of the largest particle permitted, and the distribution below it follows a defined log-normal curve.

| Level | Largest particle | Typical use |
|---|---|---|
| 1000 | 1000 micron | Commercial |
| 500 | 500 micron | General industrial |
| 300 | 300 micron | Ground support equipment |
| **200** | **200 micron** | **General aerospace fluid systems** |
| **100** | **100 micron** | **Flight propulsion, common requirement** |
| 50 | 50 micron | Precision components, small orifices |
| 25 | 25 micron | Very small passages, optical |
| 10 | 10 micron | Semiconductor, ultra-high-purity |

**Non-volatile residue** is specified separately, in mass per unit area or per unit volume of rinse:

| NVR level | Limit | Use |
|---|---|---|
| A | 1.0 mg / 0.1 m^2 | General |
| **B** | **2.0 mg / 0.1 m^2** | |
| AA | 0.5 mg / 0.1 m^2 | Precision |
| **Oxygen service** | **1.0 mg / 0.1 m^2 or better, per ASTM G93** | **Ignition risk** |

**A combined specification** looks like `Level 100A`: particulate to Level 100 and NVR to Level A. Specify both; particulate alone says nothing about the hydrocarbon film that will ignite in oxygen.

**Match the level to the smallest passage.** A Level 100 requirement permits a 100 micron particle, which will plug a 300 micron orifice. The cleanliness level and the filtration rating have to be consistent with each other and with the passage being protected; see [FlowControlDevices.md](FlowControlDevices.md).

---

## Where contamination comes from

Ranked by how much it actually contributes:

1. **Manufacturing.** Machining chips, grinding swarf, blast media, weld spatter, thread debris, and the cutting fluid on all of it. This is the largest single source and it is why parts are cleaned after machining and before assembly.
2. **The tubing itself.** Drawn tube arrives with drawing lubricant on the inside. It has to be cleaned, and a long tube is hard to clean.
3. **Assembly.** Thread sealant, PTFE tape shreds, galling debris from threaded joints, fingerprints, fibres from wipes and from clothing.
4. **Welding.** Spatter, oxide from an inadequate purge (see [Welds.md](Welds.md)), and grinding debris from blending.
5. **Test and operation.** Wear particles from valves and pumps, corrosion products, seal debris, and whatever the ground support equipment brings with it.
6. **The fluid.** Propellant to MIL-PRF-26536 monopropellant grade is permitted 1 mg/L of particulate, which over a full tank load is a real mass.

**The first flush of a new system dominates everything else.** That is why systems are flushed with a temporary coarse filter before the flight filter goes in, and why the flight filter is installed at the last possible assembly step.

---

## Cleaning processes

| Process | Removes | Notes |
|---|---|---|
| **Degrease (solvent or aqueous)** | Oils, greases, cutting fluid, NVR | The first step. Everything else depends on it |
| **Alkaline wash** | Organic soils | Aqueous, environmentally benign, needs thorough rinsing |
| **Acid pickle** | Oxide scale, heat tint | Nitric-hydrofluoric for stainless. Aggressive; can over-etch |
| **Passivation** | Free iron, restores the chromium oxide film | See [Passivation.md](Passivation.md). Not a cleaning step |
| **Ultrasonic** | Particulate from complex geometry and blind features | Reaches where flushing does not. Cavitation can damage soft parts |
| **Vapor degrease** | NVR | Very effective; most classic solvents are now restricted |
| **High pressure flush** | Loose particulate | Circulate filtered fluid at above the operating velocity |
| **Purge and dry** | Moisture | Dry GN2 to a specified dew point |
| **Electropolish** | Everything, by removing the surface | Also improves the surface for future cleanliness |
| **Bake out** | Adsorbed moisture and volatiles | Vacuum bake for high vacuum and catalyst hardware |

**Solvent selection** has changed substantially. Trichloroethylene, 1,1,1-trichloroethane and CFC-113 were the aerospace standards and are now restricted or banned. Current options are HFE (hydrofluoroethers), HFC, aqueous alkaline systems, and isopropanol. **Verify the solvent is compatible with the service fluid**, and note that any solvent residue is itself NVR.

**Rinse water quality matters.** Deionized water, and verify by the conductivity of the final rinse. Tap water leaves chlorides, and chlorides on stainless plus stress plus temperature is the recipe for SCC.

---

## Oxygen cleaning

Oxygen systems get a separate and much more stringent process, because **contamination in an oxygen system is an ignition source rather than a nuisance.**

ASTM G93 defines cleanliness levels specifically for oxygen service. The additional requirements over general aerospace cleaning:

- **NVR limits are tighter** and are the governing requirement rather than particulate
- **No hydrocarbon solvents at any stage**, because the residue is the hazard
- **Cleaning materials must themselves be oxygen compatible**: no hydrocarbon-based wipes, no ordinary gloves, no shop air (which carries compressor oil)
- **Verification is mandatory and documented**, typically by solvent rinse and gravimetric NVR, plus black light inspection for fluorescent hydrocarbons
- **Packaging immediately** in a verified-clean bag, double bagged, with the caps installed
- **The bag is opened only in a controlled environment**, at the point of installation

**The failure mode is direct:** a hydrocarbon film on the inside of a GOX line has an autoignition temperature around 500 K in oxygen, which adiabatic compression on valve opening exceeds easily. That is a fire in the line, and in an oxygen-enriched environment the line itself then burns.

**SAE ARP1176** covers oxygen system component cleaning and packaging and is the practical reference for the process.

---

## Verification

| Method | Measures | Notes |
|---|---|---|
| **Solvent rinse, filtered, particle count** | Particulate by size distribution | The standard method. Rinse a defined area, filter the rinse, count under a microscope or by automatic counter |
| **Solvent rinse, gravimetric** | NVR | Evaporate the rinse and weigh the residue |
| **Black light (UV) inspection** | Fluorescent hydrocarbons | Fast, qualitative, catches gross oil contamination. Not all hydrocarbons fluoresce |
| **Water break test** | Surface film | A clean metal surface holds a continuous water film; a contaminated one breaks it into droplets. Simple and effective |
| **Dew point** | Moisture in a purge stream | The standard moisture verification |
| **Wipe test** | Surface particulate and residue | Rub a defined area with a clean wipe and inspect |
| **Borescope** | Internal surface condition | The only way to see inside a welded assembly |

**Verify at the part level, and again at the system level after assembly.** A part that was clean and an assembly that is clean are different claims.

**Specify the rinse area and the rinse volume.** A particle count without a defined sampled area is a number with no units.

---

## Maintaining cleanliness

Cleaning is easy; **staying clean is the hard part.**

**Packaging.** Immediately after cleaning and verification, cap every port and double bag the part in a verified-clean bag. Label with the cleanliness level, the date and the process record.

**Controlled environment.** Assembly of a clean system happens in a controlled area: a cleanroom for the demanding cases, a controlled bench with filtered air for most. The environment classification (ISO 14644) should match the cleanliness requirement.

**Personnel.** Clean gloves changed frequently, lint-free garments, no cosmetics, no loose items. Fingerprints are both NVR and a chloride source.

**Tools.** Dedicated, cleaned tools. A wrench that has been used on a hydraulic system carries oil. Stainless brushes that have touched carbon steel embed iron.

**Purge gas.** Filtered and dried to a specified dew point, from a clean source. **Shop air is never acceptable**; it carries compressor oil and water.

**Open time.** Minimize the time a clean system is open. Cap ports the moment a connection is broken and do not remove the cap until the mating part is ready.

**Cleanliness is a schedule item.** A system opened for a modification has to be re-cleaned and re-verified, and that takes time that programs consistently underestimate.

---

## Design for cleanability

Cleanliness is designed in, not inspected in:

| Design feature | Effect |
|---|---|
| **Avoid blind holes and dead legs** | They trap cleaning solution and contamination and cannot be verified |
| **Avoid crevices** | A socket weld crevice cannot be cleaned. See [Welds.md](Welds.md) |
| **Provide drain paths** | A system that cannot drain cannot be flushed |
| **Smooth internal surfaces** | Electropolished or drawn tube holds far less than an as-cast or as-built additive surface |
| **Design for flushing velocity** | The flush has to reach the operating velocity or higher to lift particles |
| **Accessible ports for verification** | A rinse sample has to be takeable |
| **Minimize joint count** | Every joint made is a contamination event |
| **Weld rather than thread** | Threads generate debris on every make-up |

**Additively manufactured internal passages are a specific problem.** As-built LPBF surfaces are rough, they hold partially sintered powder, and internal passages cannot be inspected or fully cleaned. Powder removal is a qualification activity in its own right, and residual powder in a fluid system is loose particulate waiting to migrate. Abrasive flow machining, chemical polishing or sacrificial-support designs are all used; none of them are free.

---

## Design rules of thumb

| Rule | Value | Why |
|---|---|---|
| Specify particulate AND NVR | Always | Level 100A, not Level 100 |
| Cleanliness level vs smallest passage | Level number <= passage / 3 | A Level 100 particle plugs a 300 micron hole |
| Clean at the part level | Always | An assembled system cannot be cleaned properly |
| Flush velocity | >= operating velocity | Lower will not lift particles |
| Purge gas | Filtered, dried, never shop air | Compressor oil and water |
| Rinse water | Deionized, verify by conductivity | Chlorides cause SCC |
| Oxygen cleaning | ASTM G93, no hydrocarbon solvents at any stage | The residue is the hazard |
| Cap immediately | Every port, every time | Minutes of exposure undoes hours of cleaning |
| Flight filter installed last | Always | The first flush carries the construction debris |
| No blind holes, no dead legs, no crevices | Design rule | Cannot be cleaned or verified |
| Re-clean after any opening | Always | And schedule for it |

---

## Failure modes

**Orifice plugging.** A single particle in an injector element or a trim orifice. The most common contamination failure and often the first symptom of a cleanliness process breakdown.

**Valve seat damage.** A hard particle trapped between a seat and a poppet. The valve leaks permanently thereafter.

**Catalyst bed poisoning and abrasion.** Particulate abrades granules and generates fines; chemical contamination poisons active sites. See [CatalystBeds.md](CatalystBeds.md).

**Oxygen system ignition.** Hydrocarbon residue plus adiabatic compression or particle impact. The severe case.

**Filter plugged prematurely.** By construction debris that should have been flushed out before the flight filter was installed.

**Moisture-driven failures.** Ice blocking a small passage or a relief path; nitric acid formation in N2O4; catalyst poisoning in hydrazine; corrosion everywhere.

**Chloride SCC.** From tap water rinse, from fingerprints, from PVC tape, or from a marker used on a part before welding.

**Contamination generated at assembly.** PTFE tape shreds, thread sealant, galling debris. The system was clean until it was assembled.

**Residual AM powder migration.** Sintered powder shedding from an additively manufactured passage weeks into testing.

---

## Standards

| Standard | Scope |
|---|---|
| **IEST-STD-CC1246** | Product cleanliness levels and contamination control (supersedes MIL-STD-1246) |
| **ASTM G93** | Cleaning methods and cleanliness levels for material and equipment used in oxygen-enriched environments |
| **SAE ARP1176** | Oxygen system and component cleaning and packaging |
| ASTM A380 | Cleaning, descaling and passivation of stainless steel parts, equipment and systems |
| MIL-STD-1330 | Cleaning and testing of shipboard oxygen, nitrogen and hydrogen systems |
| ISO 14644 | Cleanrooms and associated controlled environments |
| ISO 14952 | Space systems, surface cleanliness of fluid systems |
| NASA-STD-8739 series | Workmanship standards |
| KSC-C-123 | Surface cleanliness of fluid systems (NASA Kennedy) |
| ASTM F331 | Nonvolatile residue of solvent extract from aerospace components |
| ASTM F312 | Microscopical sizing and counting particles from aerospace fluids on membrane filters |

---

## Tool interface

Cleanliness enters the library through the filtration rating and the protected passage:

```python
from Filter import Filter, PROTECTION_RATIO_RECOMMENDED

element = Filter()
element.setInputs({'fluid': 'N2H4', 'filterType': 'pleated mesh', 'massFlow': 0.045,
                   'upstreamPressure': 2.3e6,
                   'protectedPassage': 0.0017,          # the smallest downstream passage
                   'allowableCleanPressureDrop': 2.0e4,
                   'contaminationLoading': 1e-3})        # kg/m^3, from the propellant spec

element.selectRating()                       # applies the 10:1 rule
element.sizeElement(requiredLife = 36000.0)  # life is the binding constraint
print(element.protectionRatio)               # verify against PROTECTION_RATIO_RECOMMENDED
```

`Line.roughness` and `utils.roughnessTable` carry the additive manufacturing surface entries, which are the ones that matter for both pressure drop and cleanability.

---

## References

1. IEST-STD-CC1246E, *Product Cleanliness Levels -- Applications, Requirements, and Determination*.
2. ASTM G93-19, *Standard Guide for Cleaning Methods and Cleanliness Levels for Material and Equipment Used in Oxygen-Enriched Environments*.
3. SAE ARP1176, *Oxygen System and Component Cleaning and Packaging*.
4. ASTM A380/A380M, *Standard Practice for Cleaning, Descaling, and Passivation of Stainless Steel Parts, Equipment, and Systems*.
5. MIL-STD-1330D, *Standard Practice for Precision Cleaning and Testing of Shipboard Oxygen, Helium, Helium-Oxygen, Nitrogen, and Hydrogen Systems*.
6. Beeson, H. and Woods, S., *Guide for Oxygen Compatibility Assessments*, NASA/TM-2007-213740.
7. NASA KSC-C-123J, *Surface Cleanliness of Fluid Systems, Specification For*.
