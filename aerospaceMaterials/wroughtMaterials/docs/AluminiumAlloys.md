[Home](../README.md) > Aluminium Alloys

# Aluminium Alloys

## Contents

- [Overview](#overview)
- [The series](#the-series)
- [The launch vehicle alloys](#the-launch-vehicle-alloys)
- [Aluminium lithium](#aluminium-lithium)
- [Weldability](#weldability)
- [Cryogenic behaviour](#cryogenic-behaviour)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Aluminium is the primary structural material of a launch vehicle by mass, because tanks dominate the structure and aluminium is the right answer for a tank: light, cheap, weldable, tough at cryogenic temperature, and available in every product form.

---

## The series

| Series | Principal alloying | Strengthening | Weldable | Use |
|---|---|---|---|---|
| 1000 | Pure | Work | Yes | Foil, conductors |
| **2000** | **Copper** | Precipitation | **Some** | **Tanks (2219), structure (2024)** |
| 3000 | Manganese | Work | Yes | Sheet, tube |
| 5000 | **Magnesium** | Work | **Yes** | **Marine, cryogenic tanks, weldments** |
| **6000** | Mg and Si | Precipitation | **Yes** | **Extrusions, general structure** |
| **7000** | **Zinc** | Precipitation | **Mostly no** | **High strength machined structure** |

**The weldability column is what decides most launch vehicle applications.** 7000 series is the strongest and it is generally not fusion weldable, so it goes into machined and fastened structure. 2219 is weldable and it goes into tanks.

---

## The launch vehicle alloys

| Alloy | Yield [MPa] | Where | Why |
|---|---|---|---|
| **2219-T87** | 350 | **Tanks, cryogenic** | Weldable, tough at 20 K, well characterised |
| **2195 (Al-Li)** | 550 | **Tanks, next generation** | 5 % lighter and 30 % stronger than 2219 |
| **6061-T6** | 276 | General structure, brackets, extrusions | Cheap, weldable, forgiving, available |
| **7075-T73** | 400 | Machined structure, fittings | High strength, SCC resistant temper |
| 7050-T7451 | 440 | **Thick machined structure** | Quench tolerant, stress relieved |
| 2024-T3 | 345 | Sheet structure | Good fatigue, damage tolerant |
| 5083-H116 | 215 | Weldments, cryogenic | Very weldable, no heat treatment |

**2219-T87 is the reference cryogenic tank alloy** and it has flown on every American launch vehicle programme of consequence. Its combination is unusual: fusion weldable, its properties improve at cryogenic temperature, and its behaviour is characterised more thoroughly than almost any other alloy.

**6061-T6 is the default for anything that is not weight critical.** It is available everywhere in every form, it welds, it machines beautifully, and it tolerates process variation.

**7050-T7451 for thick machined structure** is the specific recommendation that most often goes unmade, and the reasons are in [ThicknessEffects.md](ThicknessEffects.md) and [TemperDesignations.md](TemperDesignations.md).

---

## Aluminium lithium

**Third generation Al-Li alloys are the genuine improvement over 2219**, and 2195 is the one that matters.

| Property | 2219-T87 | 2195-T8 | Change |
|---|---|---|---|
| Density | 2840 | **2700** | **-5 %** |
| Yield | 350 | **550** | **+57 %** |
| Modulus | 73 | **76** | +4 % |
| Weldable | Yes | Yes | |

**Lithium reduces density and raises modulus simultaneously**, which is unique among alloying additions and is why the alloy class exists. Each 1 percent lithium reduces density by about 3 percent and raises modulus by about 6 percent.

**The Space Shuttle Super Lightweight Tank was the demonstration**, replacing 2219 with 2195 and saving 3400 kg.

**The costs are real.** Al-Li is more expensive, more anisotropic, and more difficult to machine and to weld. Its short transverse properties are noticeably worse than 2219's, and delamination on thick section machining is a known problem.

---

## Weldability

| Alloy | Fusion weldable | Notes |
|---|---|---|
| **2219** | **Yes** | The reason it is the tank alloy |
| 6061 | Yes | With 4043 or 5356 filler |
| 5083, 5456 | **Yes** | Non heat treatable, so no HAZ strength loss beyond the work |
| **2024** | **No** | Hot cracking |
| **7075** | **No** | Hot cracking |
| 7050 | No | |

**7000 series is not fusion weldable** because the zinc-magnesium eutectic makes it hot short: the last liquid to freeze in the weld pool is a low melting film that tears under solidification shrinkage.

**Friction stir welding changes this** and it welds 2024 and 7075 successfully, because there is no melting. That is the technology that has made high strength aluminium weldments possible, and it is why FSW has become the launch vehicle tank process. See [joiningProcesses](../../joiningProcesses/).

**Heat treatable alloys lose strength in the HAZ regardless of the process** because the heat overages the precipitates. 6061-T6 as-welded yields around 138 MPa against 276 in the parent, a 50 percent knockdown, and that is the number that has to go into the joint design. It agrees with `Weld.HAZ_KNOCKDOWN` in [fluidSystems](../../../fluidSystems/).

---

## Cryogenic behaviour

**Aluminium's properties improve at cryogenic temperature and it has no ductile-to-brittle transition**, which is the FCC crystal structure at work.

| Temperature | 2219-T87 yield | Elongation |
|---|---|---|
| 293 K | 350 MPa | 10 % |
| 77 K | ~415 MPa | 13 % |
| **20 K** | **~440 MPa** | **14 %** |

**Strength and ductility both rise**, which is rare and is what makes aluminium and austenitic stainless the two cryogenic structural families.

**There is no DBTT because there is no BCC structure** to undergo the transition. That is why ferritic steels are prohibited at cryogenic temperature and aluminium is not.

See [fluidSystems CryogenicSystems.md](../../../fluidSystems/fluidSystemsLibrary/docs/CryogenicSystems.md) for the system view.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| 2219-T87 for cryogenic tanks | The reference alloy |
| 2195 Al-Li for the next step | 5 % lighter, 57 % stronger, harder to work |
| 6061-T6 as the default | Cheap, available, forgiving |
| 7050-T7451 for thick machined structure | Quench tolerant and stress relieved |
| 7000 series is not fusion weldable | Hot cracking. Use FSW |
| 6061-T6 as-welded | 138 MPa, a 50 % knockdown |
| Properties improve at cryogenic temperature | And there is no DBTT |

---

## Failure modes

**7075 fusion welded.** Hot cracking.

**As-welded 6061 designed at parent properties.** Twice the actual strength assumed.

**7075-T6 under sustained ST tension.** SCC.

**Al-Li substituted for 2219 without requalifying the weld process.** Different behaviour.

**7075 used in 100 mm plate.** Quench sensitive; 7050 is the alloy.

**Ferritic fastener in a cryogenic aluminium joint.** DBTT.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM B209 / B211 / B221** | Aluminium sheet and plate, bar, extrusion |
| **AMS 2770** | Heat treatment of wrought aluminium alloy parts |
| ANSI H35.1 | Alloy and temper designation |
| AMS-QQ-A-250 | Aluminium plate by alloy |
| ASTM G47 | SCC testing of 2XXX and 7XXX, ST direction |
| AWS D17.1 | Fusion welding for aerospace |
| MMPDS | Allowables |

---

## Tool interface

```python
import sys
sys.path.insert(0, '../aerospaceMaterialsLibrary')

from MaterialDatabase import queryMaterial

for temperature in (293.0, 77.0, 20.0):
    record = queryMaterial('2219-T87', 't87', temperature = temperature, basis = 'A')
    print(f'{temperature:5.0f} K  yield {record["yieldStrength"]/1e6:6.0f} MPa')
```

---

## References

1. MMPDS-2023, *Metallic Materials Properties Development and Standardization*.
2. Rioja, R. J. and Liu, J., "The Evolution of Al-Li Base Products for Aerospace and Space Applications", *Metallurgical and Materials Transactions A*, Vol. 43, 2012.
3. ASM Handbook Volume 2, *Properties and Selection: Nonferrous Alloys*.
