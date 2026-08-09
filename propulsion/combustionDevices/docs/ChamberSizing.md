[Home](../README.md) > Chamber Sizing

# Chamber Sizing

## Contents

- [Overview](#overview)
- [Characteristic length](#characteristic-length)
- [Residence time cancels](#residence-time-cancels)
- [Contraction ratio](#contraction-ratio)
- [What cooling actually constrains](#what-cooling-actually-constrains)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Chamber sizing is a short calculation with a long-standing piece of folklore attached, and this document exists partly to correct the folklore with numbers.

The folklore is that cooling sizes the chamber: that `L*` sets a minimum and real chambers are longer because the jacket needs the area. **That is sometimes true and it is not the general case**, and the version of it that appears in most texts, including an earlier draft of this sub-domain's own README, does not survive being computed.

---

## Characteristic length

```
Vc = L* At
```

`L*` is the chamber volume per unit throat area, and it is a proxy for the residence time combustion needs. Propellant dependent, because what is being bought is reaction time:

| Combination | `L*` [m] | Why |
|---|---|---|
| N2O4/MMH | 0.80 | Hypergolic, so ignition delay is not in the budget |
| LOX/LH2 | 0.90 | Fast kinetics and the gas is moving quickly |
| LOX/ethanol | 1.00 | Well behaved, forgiving of a short chamber |
| LOX/LCH4 | 1.05 | Between hydrogen and kerosene, as in most things |
| LOX/RP-1 | 1.10 | Kerosene needs the time, and soot does not help |
| H2O2/RP-1 | 1.50 | Decomposition then combustion, two steps in series |

It is a crude parameter. It says nothing about the shape of the volume, nothing about the injector that has to fill it, and it is a floor rather than an optimum.

---

## Residence time cancels

The result that makes `L*` easier to reason about than it looks. Substituting `At = mdot c* / Pc` and the chamber gas density `rho = Pc / (R Tc)` into `t = Vc rho / mdot`:

```
t = L* c* / (R Tc)
```

**Both chamber pressure and mass flow cancel.** Residence time is a property of the propellant and the characteristic length, and of nothing else.

A 10 kN engine and a 1000 kN engine on LOX/RP-1 at `L*` = 1.10 m both hold their propellant for **1.47 ms**. So do the same engines at 5 MPa and at 30 MPa.

Two consequences worth carrying.

**Chamber pressure is not a lever on residence time.** Attempting to fix a combustion problem by raising or lowering it will not work, and the attempt costs a design cycle.

**Scaling an engine does not change its combustion time.** A larger engine is not more forgiving of a slow-burning propellant, which is the opposite of the usual intuition about scale.

A liquid engine holds its propellant for single-digit milliseconds. Anything orders away from that is a units error, which is how an early version of this repository produced 1100 ms and survived a glance, because 1100 is a plausible-looking number when you expect milliseconds.

---

## Contraction ratio

Chamber cross-section over throat area, typically 2 to 5.

**Below about 2** the chamber gas is moving fast enough that the pressure drop from the injector face to the throat is a real performance loss, and the injector sees a lower pressure than the nominal chamber pressure.

**Above about 5** the chamber is mass that is not doing anything, and the extra wall area is extra heat load.

Large engines sit at the low end because the throat is already large; small engines at the high end because there has to be somewhere to put the injector.

**There is a hard incompatibility worth checking.** A large contraction ratio with a short `L*` leaves the convergent section consuming the whole chamber volume, and there is no barrel left to mount an injector on. The tool raises rather than returning a negative barrel length, because a negative length propagating into a mass estimate is worse than an error.

---

## What cooling actually constrains

Here is the correction to the folklore.

The [propulsion hub](../../docs/EngineSizing.md) compares a required wall area against an available one and reports which governs. With the hub's placeholder flux that check said characteristic length governed below roughly 16 MPa and cooling above it. **Computing the heat load properly changes the framing rather than the answer.**

The real constraint is not an area shortfall. The flux is computed *from* the geometry, so there is no mismatch to find: whatever wall exists rejects whatever Bartz says it rejects. The binding constraint is on the coolant side, and it is a capability limit rather than a geometric one.

For the worked example chamber at 10 MPa, the circuit fails by 89 K on coolant outlet temperature while the geometry is entirely adequate. **The chamber is the right size and the cooling still does not close.**

So the honest statement is:

- **`L*` sizes the chamber.** It is a floor and chambers are usually built near it.
- **Cooling does not size the chamber. It decides whether the design is feasible at all**, and when it fails the answer is film cooling, a lower chamber pressure or a different coolant rather than a longer chamber.

A longer chamber does add wall area, but it adds heat load with it, so lengthening a chamber to fix a cooling problem makes the problem slightly worse. That is the part the folklore gets backwards.

See [RegenerativeCooling](RegenerativeCooling.md) for where the constraint actually binds.

---

## Design rules of thumb

- **Take `L*` from the propellant and treat it as a floor.**
- **Do not try to change residence time with chamber pressure or scale.** It cancels.
- **Keep contraction ratio between 2 and 5**, low for large engines.
- **Check that the convergent section fits inside the chamber volume.**
- **Do not lengthen a chamber to solve a cooling problem.** It adds load with the area.
- **Sanity check residence time against single-digit milliseconds.** Anything else is a units error.

---

## Failure modes

**Residence time computed as a length.** Volume over area is a length, and 1100 is plausible if you are expecting milliseconds.

**Chamber pressure adjusted to change residence time.** It cancels, and the cycle is wasted.

**A chamber lengthened to fix cooling.** Adds heat load with the area and makes the problem marginally worse.

**Contraction ratio too large for the characteristic length.** No barrel left for the injector.

**`L*` treated as an optimum rather than a floor.** It is a minimum for complete combustion and there is no benefit in exceeding it.

---

## Worked numbers

The [worked example](../codeInterface.py) chamber, 100 kN LOX/RP-1 at 10 MPa, `L*` 1.10 m, contraction ratio 2.5.

| Quantity | Value |
|---|---|
| Throat diameter | 90.6 mm |
| Chamber diameter | 143.2 mm |
| Barrel length | 409.1 mm |
| Convergent length | 45.6 mm |
| Chamber volume | 7086 cm^3 |
| Residence time | 1.47 ms |
| Residence time at 5 MPa | 1.47 ms |
| Residence time at 1000 kN | 1.47 ms |

---

## Standards

| Standard | What it gives you |
|---|---|
| NASA SP-125 | Design of liquid propellant rocket engines, the sizing chapters |
| NASA SP-8087 | Fluid-cooled combustion chambers |
| NASA SP-8089 | Injectors, which set what the chamber has to accommodate |
| Huzel and Huang | The practical `L*` tables |

---

## Tool interface

Chamber geometry comes from the [propulsion hub](../../docs/EngineSizing.md), and this sub-domain consumes it.

```python
import sys
sys.path.insert(0, '../propulsionLibrary')    # from the sub-domain directory

from EngineSizing import EngineSizing

sizing = EngineSizing()
sizing.setInputs({'combination': 'LOX/RP-1', 'thrust': 100000.0,
                  'chamberPressure': 10.0e6, 'areaRatio': 20.35,
                  'contractionRatio': 2.5})

chamber = sizing.sizeChamber()
print(chamber['residenceTime'], chamber['barrelLength'])
```

---

## References

- NASA SP-125, *Design of Liquid Propellant Rocket Engines*
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
- NASA SP-8087, *Liquid rocket engine fluid-cooled combustion chambers*
- Sutton and Biblarz, *Rocket Propulsion Elements*, chapter 8
