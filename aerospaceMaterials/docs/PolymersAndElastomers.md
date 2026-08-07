[Home](../README.md) > Polymers and Elastomers

# Polymers and Elastomers

## Contents

- [Overview](#overview)
- [Glass transition is the governing property](#glass-transition-is-the-governing-property)
- [The elastomer families](#the-elastomer-families)
- [Structural polymers](#structural-polymers)
- [Permeation](#permeation)
- [Outgassing](#outgassing)
- [Compression set and stress relaxation](#compression-set-and-stress-relaxation)
- [Explosive decompression](#explosive-decompression)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

This document covers the polymer science: what a glass transition is, why permeation happens, what outgassing measures. The **selection tables live elsewhere and are not repeated here**.

For fluid compatibility by propellant, see [fluidSystems MaterialsCompatibility.md](../../fluidSystems/fluidSystemsLibrary/docs/MaterialsCompatibility.md). For gland design, squeeze, extrusion and the seal material database itself, see [fluidSystems Seals.md](../../fluidSystems/fluidSystemsLibrary/docs/Seals.md), which is where `Seal.SEAL_MATERIALS` lives. Copying that table here would create exactly the drift this repository works to avoid.

---

## Glass transition is the governing property

An elastomer seals because it is compliant. Compliance comes from long polymer chains sliding past each other, and that motion stops below the **glass transition temperature**.

**Below `Tg` an elastomer is not a soft seal. It is a hard plastic ring with no sealing compliance at all.**

| Material | Tg [K] | Practical low limit |
|---|---|---|
| Silicone | 150 | 170 K |
| **PTFE** | 160 | 20 K (not an elastomer; it is a thermoplastic) |
| EPDM | 218 | 230 K |
| Butyl | 205 | 220 K |
| **FKM (Viton)** | **255** | **255 K** |
| FFKM (Kalrez) | 268 | 270 K |

**FKM at 255 K is the one that catches people.** A Viton-sealed joint passes every ambient leak check and leaks on a cold morning, let alone at cryogenic temperature. It is the single most common cold-weather seal failure.

**The practical limit is above `Tg`, not at it.** Chain mobility falls off well before the transition, so a seal is already stiffening tens of degrees above the nominal value. Treat `Tg` as an absolute floor, not a service limit.

---

## The elastomer families

Selection by fluid is in the fluidSystems document. What matters here is the mechanism behind the behaviour.

| Family | Backbone | Why it behaves as it does |
|---|---|---|
| **FKM** | Fluorocarbon | Carbon-fluorine bonds resist oxidation and hydrocarbon attack. Fluorine also raises `Tg` |
| **EPDM** | Saturated hydrocarbon | No double bonds to attack, so it resists hydrazine and peroxide. Swells badly in hydrocarbons |
| **NBR** | Nitrile butadiene | Cheap, good in hydrocarbons, and the residual unsaturation makes it vulnerable to oxidisers |
| **FFKM** | Perfluoroelastomer | Fully fluorinated. Chemically inert to nearly everything, and very expensive |
| **Silicone** | Siloxane | The Si-O backbone gives the widest temperature range and poor chemical and tear resistance |

**The EPDM and FKM conflict is the classic bipropellant problem.** EPDM survives hydrazine and swells in hydrocarbons; FKM is the reverse. A system that carries both needs different seals in different places and a part numbering discipline that keeps them there.

**Control seal materials by part number, not by description.** Two o-rings that look identical and are described identically in a drawing note can be different compounds, and the difference is a leak.

---

## Structural polymers

| Material | Continuous use | Where it belongs |
|---|---|---|
| **PTFE** | 20 to 530 K | Seals, liners, low friction bearings. Cold flows under load |
| PCTFE | 20 to 400 K | Cryogenic seals. Better creep resistance than PTFE |
| **PEEK** | to 520 K | Structural bearings, seal backups, valve seats |
| **Vespel (polyimide)** | to 570 K | Bearings, bushings, thermal isolators. Absorbs moisture |
| G-10 fibreglass | 4 to 400 K | Cryogenic structural supports. Very low conductivity |

**PTFE cold flow is the property that surprises people.** Under sustained compressive load it creeps continuously at room temperature, so a PTFE seal loses its squeeze over months. Filled grades (glass, carbon, bronze) reduce it substantially at the cost of some chemical resistance.

**G-10 is the cryogenic structural support material** because its thermal conductivity is around 0.5 W/m-K against 16 for stainless, so a G-10 strut is a structural member that is also a thermal break.

---

## Permeation

**Permeation is the leak rate you get from a seal that is not leaking.** Gas dissolves into the elastomer on the high pressure side, diffuses through, and comes out the other side. No amount of squeeze stops it, because it is not going around the seal.

```
Q = P * A * dp / t
```

with `P` the permeability coefficient, `A` the exposed area, `dp` the pressure difference and `t` the diffusion path length.

**It scales with the exposed area and inversely with the cross section**, so a large diameter thin o-ring permeates more than a small thick one at the same pressure.

**Helium permeates fastest** because the molecule is small, which is inconvenient because helium is also the leak test tracer. A helium leak check on an elastomer-sealed joint measures permeation plus leakage, and separating the two requires calculating the permeation and subtracting it. A measured rate that matches the calculated permeation means the joint is not leaking.

**For a long duration spacecraft, permeation is the leak rate that matters.** A joint that is perfectly tight still loses its pressurant over years, and metal seals exist largely because of this.

---

## Outgassing

In vacuum, polymers release volatiles that condense on cold surfaces. On a spacecraft that means optics, radiators and solar arrays.

**ASTM E595 is the screening test** and it produces two numbers:

| Metric | Meaning | Limit |
|---|---|---|
| **TML** | Total mass loss | **< 1.0 %** |
| **CVCM** | Collected volatile condensable material | **< 0.10 %** |

**CVCM is the one that matters** for contamination, because it measures what actually deposits on a cold surface rather than what merely leaves the part.

**A vacuum bake before flight reduces both**, and it is standard practice for anything polymeric going into a sensitive spacecraft. The bake drives off the volatiles on the ground rather than in orbit onto a mirror.

**Silicones are the classic problem.** Many silicone formulations have high CVCM and the deposited film is difficult to remove. Low outgassing silicone grades exist and have to be specified explicitly.

---

## Compression set and stress relaxation

**Compression set** is the permanent deformation retained after a seal is compressed and released. It is what turns a round o-ring into a flat one and it directly consumes the squeeze the seal depends on.

**Stress relaxation** is the decay of sealing force at constant compression. It is the same underlying viscoelastic mechanism measured the other way round, and it is the more directly relevant number for a static seal.

Both accelerate with temperature, following an Arrhenius relation, which is what makes accelerated seal life testing possible. The [`LifeTest`](../../fluidSystems/fluidSystemsTesting/fluidSystemsTestingLibrary/LifeTest.py) class in fluidSystemsTesting handles that acceleration, and the activation energy is the assumption everything rests on.

---

## Explosive decompression

An elastomer under high pressure gas absorbs it. **Depressurise rapidly and the dissolved gas expands faster than it can diffuse out, blistering or splitting the seal from the inside.**

| Control | Effect |
|---|---|
| **Slow depressurisation** | The primary control. Rate limits are seal specific |
| Harder compound | Resists internal pressure better |
| Lower gas solubility | FKM is worse than EPDM for CO2 |
| Smaller cross section | Shorter diffusion path out |

It is a failure mode of high pressure gas systems specifically, and it is why a rapid blowdown procedure needs a seal review rather than only a structural one.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Tg is an absolute floor, not a service limit | Allow 15 to 30 K above it |
| FKM stops sealing at 255 K | The commonest cold weather failure |
| Control seal material by part number | Descriptions are not specifications |
| Permeation is not leakage | Calculate it before chasing a leak |
| CVCM below 0.10 percent for spacecraft | And vacuum bake anyway |
| PTFE cold flows | Filled grades or a metal backup |
| G-10 for cryogenic structural supports | 0.5 W/m-K against 16 for stainless |
| Slow depressurisation on high pressure gas | Explosive decompression |
| Never reuse an elastomer seal | Compression set has consumed the squeeze |

---

## Failure modes

**A Viton seal below 255 K.** Glassy, no compliance, leaks immediately.

**Permeation mistaken for a leak.** Hours chasing a joint that is tight.

**Compression set from a reused seal.** The squeeze is gone before installation.

**Explosive decompression after a rapid blowdown.** Blisters and splits from the inside.

**Silicone outgassing onto an optic.** A deposited film that cannot be cleaned in orbit.

**PTFE creeping out of its gland.** Cold flow under sustained load.

**The wrong elastomer in a bipropellant system.** EPDM in the fuel, FKM in the oxidiser, and a mix-up in the stores.

---

## Standards

| Standard | Scope |
|---|---|
| **ASTM E595** | Total mass loss and collected volatile condensable materials in vacuum |
| **ASTM D395** | Rubber compression set |
| ASTM D1414 | Rubber o-rings, test methods |
| ASTM D2000 | Classification system for rubber products |
| ASTM D573 | Rubber deterioration in an air oven |
| **AMS 7276 / 7259** | FKM and EPDM o-ring compounds |
| SAE AS568 | O-ring sizes |
| NASA-STD-6001 | Flammability, offgassing and compatibility |
| ASTM D1434 | Gas permeability of plastic film and sheeting |
| **NORSOK M-710** | Elastomer qualification including explosive decompression |

---

## Tool interface

The seal material database and the gland sizing live in fluidSystems and are not duplicated here.

```python
# the rejection below is the point of the example, so it is caught
try:
    import sys
    sys.path.insert(0, '../fluidSystems/fluidSystemsLibrary')

    from Seal import Seal

    seal = Seal()
    seal.setInputs({'sealType': 'static face', 'material': 'fkm',
                    'crossSectionDiameter': 0.00178, 'designPressure': 2.5e6,
                    'minimumTemperature': 240.0, 'fluid': 'N2H4'})
    seal.checkCompatibility()      # raises on the glass transition violation at 240 K
    seal.calculatePermeation('He') # the leak rate from a seal that is not leaking
except Exception as error:
    print('rejected as expected: {}'.format(type(error).__name__))
```

Lookup table: `Seal.SEAL_MATERIALS`, which is the single source for elastomer properties in this repository.

---

## References

1. Parker Hannifin, *Parker O-Ring Handbook*, ORD 5700.
2. ASTM E595-15, *Standard Test Method for Total Mass Loss and Collected Volatile Condensable Materials from Outgassing in a Vacuum Environment*.
3. Ferry, J. D., *Viscoelastic Properties of Polymers*, 3rd ed., Wiley, 1980.
4. Campion, R. P., "Elastomer Seals for High Pressure Gas Service", *Sealing Technology*, 2006.
5. NASA Outgassing Database, https://outgassing.nasa.gov.
