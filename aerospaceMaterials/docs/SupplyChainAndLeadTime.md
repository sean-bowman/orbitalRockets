[Home](../README.md) > Supply Chain and Lead Time

# Supply Chain and Lead Time

## Contents

- [Overview](#overview)
- [Lead time is a material property](#lead-time-is-a-material-property)
- [Mill forms and minimum orders](#mill-forms-and-minimum-orders)
- [Relative cost](#relative-cost)
- [Why cost data rots](#why-cost-data-rots)
- [Single source and sole source](#single-source-and-sole-source)
- [Counterfeit and misrepresentation](#counterfeit-and-misrepresentation)
- [Obsolescence](#obsolescence)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A material that cannot be bought in time is not a candidate, and a material with one supplier is a programme risk regardless of its properties.

This is treated as a materials topic rather than a procurement one because the decision that creates the problem is a materials decision, taken months before anyone tries to buy anything.

---

## Lead time is a material property

Typical, from order to delivery, for a standard mill form in a normal market.

| Material | Sheet | Plate | Bar | Forging | Tube |
|---|---|---|---|---|---|
| **6061** | 3 | 4 | 2 | 16 | 3 |
| 7075 | -- | 5 | 4 | 20 | -- |
| 2024 | 6 | 8 | 6 | -- | -- |
| **2219** | 14 | 18 | 12 | 30 | -- |
| **2195 (Al-Li)** | 30 | **32** | -- | 44 | -- |
| **316L** | 3 | 4 | 3 | 16 | 4 |
| 321 | 6 | 8 | 6 | -- | 8 |
| 17-4PH | -- | 10 | 6 | 20 | -- |
| A286 | -- | -- | 12 | 26 | -- |
| **Ti-6Al-4V** | 12 | 16 | 10 | **30** | -- |
| Ti-6Al-4V ELI | 18 | 22 | 16 | 36 | -- |
| **Ti-3Al-2.5V** | -- | -- | 16 | -- | **20** |
| Inconel 718 | 16 | 20 | 14 | 32 | -- |
| Inconel 625 | 14 | 18 | 12 | -- | 16 |
| **Haynes 230** | 26 | 30 | 24 | -- | -- |
| **GRCop-42 powder** | -- | -- | -- | -- | 14 |

All figures in weeks, indexed to a 2026-Q1 basis.

**The spread is a factor of sixteen** between 6061 bar at 2 weeks and 2195 plate at 32. A design that switches from 6061 to 2195 late in the programme has added eight months to the critical path, and the mass saving that motivated it is usually worth less than the schedule.

**Forgings roughly double the lead time** over bar, because die manufacture sits ahead of the forging itself. A closed die forging is a 30 to 44 week item and it belongs on the long lead list from the start.

**A tight market changes everything.** These are normal-market figures; titanium and nickel lead times have historically doubled during demand surges, and the surge is not predictable.

---

## Mill forms and minimum orders

| Form | Typical minimum |
|---|---|
| Sheet and plate | One full plate, often 1.2 x 2.4 m |
| Bar | One full length, 3 to 6 m |
| **Tube** | **Mill run, often 300 m or more** |
| Forging | One die set, plus a minimum piece count |
| Powder | One batch, 50 to 250 kg |

**Tube is the one that surprises people.** A mill will not run a special size for a small quantity, so a programme needing a non-standard titanium tube faces either a mill run or a distributor who happens to hold it. **Design to standard tube sizes** unless there is a compelling reason not to; the fluidSystems [`Line`](../../fluidSystems/fluidSystemsLibrary/Line.py) class selects from standard sizes for exactly this reason.

**Powder minimums matter for additive.** A 250 kg minimum on a specialist alloy is a real commitment when the part weighs 2 kg, and it drives the decision to use a service bureau that already stocks it.

**Buying from a distributor rather than a mill** trades cost for availability and for lot size. Distributors hold common forms in common alloys, and they hold them in whatever lots the mill supplied, so a distributor order may span several heats. For a fracture critical part that is a traceability complication.

---

## Relative cost

Indexed to 316L bar at 1.0. **These are ratios and there are no currency figures anywhere in this repository**, for reasons in the next section.

| Material | Relative cost |
|---|---|
| 4340 | 0.4 |
| **6061** | **0.6** |
| 300M | 0.9 |
| 7075 | 0.9 |
| **316L** | **1.0** |
| 2024 | 1.1 |
| 7050 | 1.2 |
| 2219 | 1.4 |
| 347 | 1.4 |
| 17-4PH | 1.6 |
| A286 | 3.2 |
| CP Ti grade 2 | 4.0 |
| **2195 (Al-Li)** | **4.5** |
| Monel 400 | 5.5 |
| C18150 | 6.0 |
| AlSi10Mg powder | 6.0 |
| **Inconel 718** | **6.5** |
| Inconel 625 | 7.0 |
| Monel K-500 | 8.0 |
| **Ti-6Al-4V** | **8.5** |
| Ti-3Al-2.5V | 9.0 |
| Hastelloy X | 11.0 |
| Ti-6Al-4V ELI | 11.0 |
| IM7/8552 prepreg | 12.0 |
| **Haynes 230** | **14.0** |
| NARloy-Z | 18.0 |
| T1000G towpreg | 20.0 |
| **GRCop-42 powder** | **22.0** |

**Material cost is rarely the dominant cost of a part.** Buy-to-fly, machining time and inspection usually exceed it. The ratio matters most where buy-to-fly is high: 8:1 machining on an alloy at 8.5 makes the stock cost 68 times a 6061 near-net part.

---

## Why cost data rots

**Absolute prices are wrong within a quarter.** Metal prices move with energy costs, alloying element availability, freight and demand, and none of those are stable.

**Ratios move too, just more slowly.** The titanium to stainless ratio has ranged between roughly 5 and 12 over the past two decades.

**Every cost figure in this repository carries a basis date** and the [`MaterialSelector`](../aerospaceMaterialsLibrary/MaterialSelector.py) prints it beside every cost figure it reports. A basis more than eighteen months old is flagged.

**Never put a currency figure in a design document.** It will be read as authoritative long after it stopped being true, and it invites a decision it cannot support. A ratio with a date is honest about what it is.

---

## Single source and sole source

**Sole source** means only one supplier exists in the world. **Single source** means only one is qualified on this programme, and others exist.

| Situation | Risk | Mitigation |
|---|---|---|
| **Sole source** | No alternative at any price | Strategic stock, or a design change |
| Single source | Others exist but are not qualified | Qualify a second source |
| Single lot | One heat behind all flight hardware | Buy the whole requirement at once |

**Qualifying a second source is a real programme, not a purchase order.** For a fracture critical material it means an equivalency campaign, which is 18 to 30 specimens plus documentation and review. Starting it after the first source has a problem is starting it too late.

**Strategic stock is the practical answer for a genuinely sole-sourced material.** Buy the programme requirement in one lot, store it under controlled conditions, and accept the working capital. It also solves the single lot traceability problem at the same time.

**Specialist materials are the usual sole sources**: GRCop-42, Al-Li plate, specific prepreg systems, and any material with a single qualified atomiser or a single mill.

---

## Counterfeit and misrepresentation

Higher value alloys attract fraud, and the aerospace supply chain has repeatedly been penetrated.

| Form | Description |
|---|---|
| **Substitution** | A cheaper alloy sold as an expensive one |
| **Falsified certificates** | Genuine material, forged paperwork on condition or heat treat |
| **Re-certification** | Rejected material re-papered and resold |
| Mixed lots | Several heats sold as one |
| Scrap re-entry | Offcuts and swarf reintroduced as virgin material |

**Controls, in order of effectiveness:**

**Buy from approved distributors with a documented chain of custody.** The single most effective control, and it is why approved supplier lists exist.

**Verify mill certificates directly with the mill** for critical material. Forged certificates are common and they look right.

**Positive material identification on incoming.** Handheld XRF distinguishes alloy families and most alloys within a family in seconds. It catches both substitution and the honest warehouse mix-up that no certificate would ever reveal.

**Full chemical analysis and mechanical testing** for fracture critical material. Expensive, and appropriate where the consequence justifies it.

---

## Obsolescence

Materials disappear, and usually for reasons nothing to do with aerospace.

| Driver | Example |
|---|---|
| **Regulatory** | Cadmium plating, chromate conversion coatings, hexavalent chromium |
| Environmental | Solvents: trichloroethylene, CFC-113, and their successors in turn |
| Market | A mill exits a low volume alloy |
| Supply | An alloying element becomes restricted or scarce |

**Regulatory obsolescence has the longest warning and is still the most disruptive**, because the replacement usually has different properties and requires re-qualification. Cadmium to IVD aluminium was a decade-long transition across the industry, and it was better than cadmium for hydrogen embrittlement anyway.

**Design out obsolescent processes rather than seeking exemptions.** An exemption is a temporary permission with an expiry date attached to a programme that may outlive it.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Lead time is a selection criterion | 2 to 32 weeks across the alloy set |
| Forgings roughly double the bar lead time | Die manufacture sits ahead of it |
| Design to standard tube sizes | The alternative is a mill run |
| Never put a currency figure in a design document | Ratios with a basis date |
| Flag cost data older than 18 months | It has moved |
| Qualify a second source before you need one | It is a campaign, not a purchase order |
| Strategic stock for sole sourced material | And it solves single lot traceability too |
| PMI on incoming critical material | Cheap, fast, and it catches warehouse errors |
| Design out obsolescent processes | Rather than seeking exemptions |

---

## Failure modes

**A design frozen on a 32 week material.** Eight months on the critical path.

**A non-standard tube size specified.** Mill run minimum, or nothing.

**A currency figure in a specification.** Read as authoritative years later.

**A sole source discovered when the supplier has a problem.** Second source qualification starts too late.

**All flight hardware from one heat.** A nonconformance scraps the fleet.

**Counterfeit material with a convincing certificate.** No PMI, no verification, no way to know.

**An exemption for an obsolescent process.** It expires before the programme does.

**Distributor material spanning several heats.** A traceability complication on a fracture critical part.

---

## Standards

| Standard | Scope |
|---|---|
| **AS6174** | Counterfeit materiel, assuring acquisition of authentic and conforming materiel |
| AS5553 | Counterfeit electronic parts, avoidance, detection, mitigation |
| **AS9100** | Quality management for aviation, space and defence |
| AS9120 | Quality management for aerospace distributors |
| **ASTM E1476** | Metal and alloy identification and analysis |
| ASTM E572 | Analysis of stainless and alloy steels by XRF |
| **NASA-STD-6016** | Materials and processes requirements, including approved material lists |
| ISO 9001 | Quality management systems |
| EN 10204 | Types of inspection document for metallic products |
| REACH / RoHS | Regulatory drivers for material and process obsolescence |

---

## Tool interface

```python
from MaterialSelector import MaterialSelector

# Lead time and cost are first class screening criteria, not an afterthought
selector = MaterialSelector()
selector.setInputs({'requirements': {'serviceTemperature': 293.15,
                                     'minimumUltimateStrength': 400.0e6,
                                     'form': 'plate',
                                     'maximumLeadTimeWeeks': 12,
                                     'maximumRelativeCost': 5.0},
                    'loadingMode': 'plate strength',
                    'weights': {'mass': 0.3, 'cost': 0.3, 'leadTime': 0.3, 'risk': 0.1}})

result = selector.screen()
for label, reasons in result['rejected'].items():
    print(label, reasons)      # every rejection names the criterion and the margin
```

Cost ratios and lead times live in `materialData.MATERIAL_DATABASE` under `relativeCost`, `costBasisDate` and `leadTimeWeeks`.

---

## References

1. SAE AS6174A, *Counterfeit Materiel; Assuring Acquisition of Authentic and Conforming Materiel*.
2. NASA-STD-6016B, *Standard Materials and Processes Requirements for Spacecraft*.
3. GAO-10-389, *Defense Supplier Base: DOD Should Leverage Ongoing Initiatives in Developing Its Program to Mitigate Risk of Counterfeit Parts*.
4. SAE AS9120B, *Quality Management Systems -- Requirements for Aviation, Space and Defense Distributors*.
5. EN 10204:2004, *Metallic Products -- Types of Inspection Documents*.
