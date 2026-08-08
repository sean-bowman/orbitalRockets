[Home](../README.md) > Heat Pipes and Two Phase

# Heat Pipes and Two Phase

## Contents

- [Overview](#overview)
- [How a heat pipe works](#how-a-heat-pipe-works)
- [The four limits](#the-four-limits)
- [Working fluid selection](#working-fluid-selection)
- [Wick selection is a transport against tilt trade](#wick-selection-is-a-transport-against-tilt-trade)
- [Ground testability](#ground-testability)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A heat pipe moves heat along a temperature difference so small it is often unmeasurable, which makes it look like a thermal short circuit and makes it very attractive on a spacecraft. It has no moving parts, no power draw and no working fluid inventory to manage.

It also has a hard capability limit, and past that limit it does not degrade. It stops.

**That is the defining property.** A conduction path that is undersized runs hotter. A radiator that is undersized runs hotter. A heat pipe past its capillary limit dries out at the evaporator, the wall temperature there rises without bound, and it does not recover until the load is reduced substantially below the limit. The design consequence is that a heat pipe needs margin rather than proximity.

---

## How a heat pipe works

Three sections and a closed cycle. Heat into the evaporator vaporises the working fluid. The vapour flows down the core to the condenser, driven by a small pressure difference. It condenses, releasing the latent heat. The liquid returns through the wick, driven by capillary pressure.

The whole device is a balance between one pressure that pushes and several that resist.

```
capillary head        2 sigma / r_pore          the pump
liquid pressure drop  mu_l L_eff m / (rho K A)  Darcy flow through the wick
vapour pressure drop                            usually small
gravity head          rho g L sin(theta)        helps or hurts, depending on tilt
```

**The pipe works while the capillary head exceeds the sum of the others.** When it does not, the wick cannot keep the evaporator wet.

The effective length is not the physical length. It is the adiabatic section plus half of each of the evaporator and condenser, because fluid enters and leaves those distributed along their length.

---

## The four limits

Four independent mechanisms can cap the transport, and which one governs changes with temperature, geometry and fluid.

**Capillary.** The wick cannot return liquid fast enough. This is the usual governing limit at ordinary operating temperatures, and it is the one that produces the dry out cliff.

**Sonic.** The vapour reaches Mach 1 at the evaporator exit. It caps the transport at a value that rises steeply with temperature, so it governs only at startup from a cold state or in liquid metal pipes. In a room temperature ammonia pipe it is three orders above the capillary limit and irrelevant.

**Entrainment.** Vapour flowing counter to the returning liquid tears droplets off the wick surface and carries them to the condenser, starving the evaporator. It is a Weber number criterion, and it matters at high vapour velocity, which means small vapour cores and high transport.

**Boiling.** Bubbles nucleate inside the wick rather than at the liquid surface, and a vapour bubble in the wick blocks liquid return locally. The criterion involves the radius at which a bubble can form, and **that is the nucleation radius of the surface, not the pore radius of the wick.**

That distinction is worth spelling out because getting it wrong is easy and the error is large. The nucleation radius is a surface property, around 2.5e-07 m, and the pore radius of an axial groove wick is 2.5e-04 m. Using the pore radius understates the boiling limit by that ratio, and the result is that boiling appears to govern a grooved ammonia pipe at 0.2 W. **It is 187 W, and capillary governs as it should.** This was a real bug in this library and it is guarded by a regression test.

---

## Working fluid selection

The figure of merit is:

```
M = rho_l sigma h_fg / mu_l      [W/m^2]
```

It combines the capillary pumping the fluid can generate, the heat it carries per unit mass, and how hard it is to push through the wick.

| Fluid | Merit number | Usable range [K] | Comment |
|---|---|---|---|
| Water | 4.55e+11 | 303 to 473 | The best there is, and it freezes at 273 K |
| Ammonia | 1.06e+11 | 213 to 373 | The spacecraft standard |
| Methanol | 4.13e+10 | 283 to 403 | Lower freezing point than water, lower performance |
| Ethane | 2.29e+10 | 150 to 300 | Cryogenic range, for detectors and cold hardware |

**Water has four times the merit of ammonia and is used on very few spacecraft.** The reason is the freezing point. A water heat pipe that freezes can burst, and if it does not burst it has to be thawed before it will start, which requires exactly the heat transport it is not providing. Ammonia at 213 K covers the whole survival range of most hardware and that is worth a factor of four.

**Operating outside the fluid range is not a degradation, it is a non-operation.** Below the range the vapour pressure is too low to drive any flow; above it the pressure is a structural problem. The class refuses rather than extrapolating.

---

## Wick selection is a transport against tilt trade

The capillary head goes as `1 / r_pore` and the permeability goes roughly as `r_pore^2`. **A finer wick pumps harder and flows worse**, and the two effects do not cancel.

| Wick | Pore radius [m] | Permeability [m^2] | Head with ammonia [Pa] |
|---|---|---|---|
| Axial groove | 2.5e-04 | 5e-09 | 170 |
| Screen mesh | 8e-05 | 3e-10 | 533 |
| Sintered metal | 3e-05 | 2e-11 | 1420 |
| Arterial | 2e-05 | 1e-09 | 2130 |

For a one metre ammonia pipe at 293 K with a 5 mm vapour radius:

| Wick | Transport in orbit [W] | Transport at 2 degrees adverse tilt [W] |
|---|---|---|
| Axial groove | 115.0 | 0 |
| Sintered metal | 3.8 | 3.3 |

**The grooved pipe carries thirty times more and dies at two degrees. The sintered pipe carries almost nothing and does not care about tilt.**

That is the trade, and it is why the axial groove is the spacecraft standard: in orbit there is no gravity head at all, so the only thing the groove gives up is worthless there. It is also why sintered wicks appear in terrestrial applications and in anything that has to work on the bench in an arbitrary orientation.

The arterial wick is the attempt to have both: a fine pore surface for pumping and a separate large liquid artery for flow. It works, and it introduces a priming failure mode, because an artery with a vapour bubble in it is not an artery.

---

## Ground testability

A heat pipe in orbit has no gravity head. A heat pipe on the bench has a large one, and the sign depends on which end is up.

```
gravity head = rho g L sin(theta)
```

For a one metre ammonia pipe, that is 51 Pa per half degree of tilt. The axial groove capillary head is 170 Pa.

| Tilt | Transport [W] |
|---|---|
| 2.0 degrees favourable | 253.5 |
| 0.5 degrees favourable | 149.6 |
| Level | 115.0 |
| 0.5 degrees adverse | 80.3 |
| 2.0 degrees adverse | 0 |
| 5.0 degrees adverse | 0 |

**Two degrees of adverse tilt takes a 115 W pipe to zero.** Two degrees of favourable tilt takes it to 253 W, which is more than twice its orbital capability.

Both directions are traps. **A pipe tested favourably was never tested**, because it demonstrated a capability it will not have in flight. A pipe tested adversely by an uncontrolled amount can fail acceptance for a reason that does not exist in orbit.

The consequence is that heat pipe bench testing requires tilt control to a fraction of a degree, and that the orbital capability is a calculation validated by test rather than a measurement.

The class reports the dead angles explicitly: the tilts at which transport is zero, which is the number a test procedure has to be written against.

---

## Design rules of thumb

- **Design to a fraction of the capillary limit.** The failure past it is a cliff, and dry out does not recover until the load drops well below the limit.
- **Use ammonia unless there is a reason not to.** The range covers most survival bands and the merit number is adequate.
- **Do not use water where it can freeze.** Bursting aside, a frozen pipe cannot thaw itself.
- **Use axial grooves in orbit and sintered wicks on the ground.** The trade inverts with gravity.
- **Control tilt to better than the dead angle during test**, and state the dead angle in the test procedure.
- **Check all four limits.** Which one governs changes with temperature, and the sonic limit governs at startup even when it is irrelevant in operation.
- **Treat an arterial wick as a priming risk**, not just a performance option.

---

## Failure modes

**Operated past the capillary limit.** Evaporator dry out, unbounded local temperature rise, no graceful degradation.

**Boiling limit computed on the pore radius.** Understates the limit by three orders and makes boiling appear to govern when it does not.

**Tested favourably.** Demonstrates a capability the pipe will not have in orbit.

**Tested adversely without measuring the tilt.** Fails hardware that is fine.

**Water pipe frozen.** Cannot restart, may burst.

**Artery not primed.** A vapour bubble in the artery removes the entire reason for having one.

**Operated outside the fluid range.** Not degraded, not working.

---

## Worked numbers

A one metre ammonia pipe, axial groove wick, 5 mm vapour radius, 0.8 mm wick, 293.15 K, level.

| Limit | Value [W] |
|---|---|
| **Capillary** | **115.0** |
| Boiling | 189.7 |
| Entrainment | 1303 |
| Sonic | 78 488 |

**Capillary governs at 115 W.** The sonic limit is 680 times higher and is not a consideration at this temperature.

| Quantity | Value |
|---|---|
| Capillary head | 170.4 Pa |
| Gravity head, level | 0 Pa |
| Net head | 170.4 Pa |
| Gravity head at 2 degrees | 205.4 Pa |
| Dead angles | 2.0 and 5.0 degrees adverse |

**The gravity head at two degrees exceeds the capillary head**, which is why the transport is exactly zero there rather than merely reduced.

The same pipe with a sintered wick:

| Limit | Value [W] |
|---|---|
| **Capillary** | **3.8** |
| Boiling | 188.3 |
| Entrainment | 3761 |
| Sonic | 78 488 |

Capillary still governs, at thirty times less. **Over one metre the sintered wick's permeability penalty is brutal**, which is why sintered pipes are usually short.

---

## Standards

| Standard | What it gives you |
|---|---|
| ECSS-E-ST-31-02C | Two phase heat transport equipment |
| NASA-HDBK-2001 | Spacecraft thermal control handbook, heat pipe chapter |
| MIL-STD-1540 | Test requirements, including thermal vacuum |
| ASTM E2739 | Standard practice for heat pipe performance testing |

---

## Tool interface

```python
from HeatPipe import HeatPipe

pipe = HeatPipe()
pipe.setInputs({'length':               1.0,
                'vapourRadius':         0.005,
                'workingFluid':         'ammonia',
                'wickType':             'axial groove',
                'wickThickness':        0.0008,
                'operatingTemperature': 293.15,
                'tiltAngle':            0.0})

limits = pipe.calculateLimits()
print(limits['governing'], limits['transportCapability'])

ground = pipe.checkGroundTestability()
print(ground['orbitalLimit'], ground['deadAngles'])
```

`checkGroundTestability` sweeps a default set of tilts and reports the angles at which transport reaches zero.

---

## References

- Faghri, *Heat Pipe Science and Technology*
- Chi, *Heat Pipe Theory and Practice*
- Gilmore, *Spacecraft Thermal Control Handbook*, volume I, chapter 14
- Peterson, *An Introduction to Heat Pipes*
- Dunn and Reay, *Heat Pipes*
