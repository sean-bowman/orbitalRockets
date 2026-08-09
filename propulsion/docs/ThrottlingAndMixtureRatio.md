[Home](../README.md) > Throttling and Mixture Ratio

# Throttling and Mixture Ratio

## Contents

- [Overview](#overview)
- [Injector authority collapses faster than thrust](#injector-authority-collapses-faster-than-thrust)
- [The nozzle separates before the injector gives up](#the-nozzle-separates-before-the-injector-gives-up)
- [What deep throttle actually costs](#what-deep-throttle-actually-costs)
- [Mixture ratio control](#mixture-ratio-control)
- [Propellant utilisation and residuals](#propellant-utilisation-and-residuals)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Throttling a liquid engine is not a matter of turning it down. Two independent things break as thrust falls, they break at different rates, and neither of them is the combustion.

The first is injector authority: the pressure drop that isolates the feed system from the chamber falls as the square of the flow, so it collapses faster than the thrust does. The second is the nozzle, which becomes progressively more over-expanded as chamber pressure falls and separates well before the injector runs out.

Mixture ratio is the other control variable, and it is the one that decides how much propellant arrives at burnout unused.

---

## Injector authority collapses faster than thrust

An injector is an orifice. Its pressure drop follows the flow squared:

```
dP_inj ~ mdot^2 / rho
```

At a fixed throat the chamber pressure is proportional to mass flow, so

```
dP_inj ~ Pc^2      and therefore      dP_inj / Pc ~ Pc
```

**The stiffness ratio falls linearly with throttle setting.** An injector designed with 20 per cent stiffness at full thrust has:

| Throttle | Injector stiffness |
|---|---|
| 100 % | 20.0 % |
| 80 % | 16.0 % |
| 60 % | 12.0 % |
| 50 % | 10.0 % |
| 40 % | 8.0 % |
| 30 % | 6.0 % |
| 25 % | 5.0 % |
| 20 % | 4.0 % |

Stiffness is what decouples the feed system from the chamber. When it is high, a chamber pressure oscillation cannot propagate upstream and modulate the flow that feeds it. When it is low, it can, and the feed system and the chamber become a single coupled oscillator.

**Below roughly 5 to 8 per cent the coupling is strong enough to sustain a chug instability.** That places a hard floor on throttling with a fixed injector:

| Stiffness floor | Deepest throttle |
|---|---|
| 8 % | 40 % |
| 5 % | 25 % |

This is why deep throttle needs a variable area injector. A pintle moves the injection area with the flow, holding `dP_inj` roughly constant instead of letting it fall as the square, and it is the reason pintle injectors appear on every engine that has to throttle deeply and land.

---

## The nozzle separates before the injector gives up

The second constraint arrives sooner and it is usually the one people miss.

Exit pressure is a fixed fraction of chamber pressure for a fixed area ratio. Throttling reduces chamber pressure and therefore exit pressure, while ambient pressure does not move. **A nozzle sized at the separation limit at full thrust separates as soon as it throttles at all.**

For the worked example engine, area ratio 20.35 at 10 MPa, at sea level:

| Throttle | `Pc` [MPa] | `Pe` [kPa] | `Pe/Pa` | Separated |
|---|---|---|---|---|
| 100 % | 10.00 | 43.37 | 0.428 | No |
| 80 % | 8.00 | 34.70 | 0.342 | Yes |
| 60 % | 6.00 | 26.02 | 0.257 | Yes |
| 50 % | 5.00 | 21.69 | 0.214 | Yes |
| 40 % | 4.00 | 17.35 | 0.171 | Yes |
| 30 % | 3.00 | 13.01 | 0.128 | Yes |

**The design point that was optimal at full thrust is separated at 80 per cent.** The injector still has 16 per cent stiffness there and is nowhere near its limit.

That is a genuine and awkward coupling. The [worked example](../codeInterface.py) selects the area ratio to maximise burn-averaged impulse subject to not separating at full thrust, and that choice quietly forecloses sea level throttling. A vehicle that throttles through max-Q, or that lands propulsively, cannot use it.

**The resolution is that the constraint is altitude dependent.** A max-Q throttle-down happens at 10 to 15 km, where ambient is a quarter of sea level and the separation limit is correspondingly further out. A landing burn happens near sea level and does not have that relief, which is one of several reasons landing engines are a different design point from ascent engines.

---

## What deep throttle actually costs

Not just performance. The list is longer than it looks.

**Combustion stability margin.** The injector is designed at one operating point and is off-design everywhere else.

**Cooling.** Heat flux falls with chamber pressure, but so does coolant flow, and the two do not fall at the same rate. Wall temperature can rise on throttle-down.

**Mixture ratio drift.** The oxidiser and fuel circuits have different pressure drop characteristics, so their flows do not scale identically. Mixture ratio shifts with throttle unless it is actively controlled.

**Turbomachinery.** A pump has a limited operating range before it stalls or cavitates, and a turbine driving it has its own. On a pump-fed engine this frequently sets the throttle floor before the injector does.

**Nozzle separation**, as above, which is a structural problem rather than a performance one.

---

## Mixture ratio control

Mixture ratio is set by the relative pressure drops of the two circuits, which means it is set by hardware unless something actively controls it.

The reasons to control it:

**Performance.** `c*` peaks near the design mixture ratio and falls either side. The penalty is second order for small excursions, which is why it is not usually the reason.

**Propellant utilisation.** This is the real reason, and it is first order. See below.

**Wall temperature.** Running fuel rich cools the chamber wall and running oxidiser rich attacks it. Mixture ratio excursions toward oxidiser rich are a hardware risk rather than a performance one.

Control is normally a valve in one circuit trimmed against measured tank levels, closing the loop on utilisation rather than on mixture ratio directly.

---

## Propellant utilisation and residuals

Tanks are loaded at the design mixture ratio. If the engine runs at a different one, one propellant runs out first and the rest of the other is dead mass carried to burnout.

For LOX/RP-1 loaded at `MR` 2.56:

| `MR` error | Actual `MR` | Residual propellant |
|---|---|---|
| -5 % | 2.432 | 3.60 % |
| -2 % | 2.509 | 1.44 % |
| 0 | 2.560 | 0 |
| +2 % | 2.611 | 0.55 % |
| +5 % | 2.688 | 1.34 % |

**The penalty is asymmetric, and running fuel rich is the expensive direction.** A 5 per cent error toward fuel rich strands 3.60 per cent of the propellant load; the same error toward oxidiser rich strands 1.34 per cent.

The reason is which propellant gets stranded. At `MR` 2.56 the oxidiser is 72 per cent of the load. Running fuel rich consumes fuel faster relative to how it was loaded, so the fuel runs out first and the stranded propellant is oxidiser, which is the larger inventory. Running oxidiser rich strands fuel, of which there is less to strand.

**Three and a half per cent of propellant is a large number.** On a stage with a mass ratio of 3 it is comparable to the entire payload. That is why propellant utilisation systems exist, and why the loading mixture ratio is sometimes deliberately biased toward the direction whose residual is cheaper.

The design mixture ratio is chosen for performance. **The loading mixture ratio is a different decision** and it is allowed to differ, biased so that the expected dispersion strands the cheaper propellant.

---

## Design rules of thumb

- **Design injector stiffness at 15 to 20 per cent** at the deepest intended throttle setting, not at full thrust.
- **Check nozzle separation across the whole throttle range**, at the ambient pressure it will be used at.
- **Expect the nozzle to constrain sea level throttling before the injector does.**
- **Use a variable area injector for anything below about 40 per cent** on a fixed-area design.
- **Check wall temperature on throttle-down**, not only at full thrust. Coolant flow falls too.
- **Control utilisation, not mixture ratio.** The tank levels are what matter at burnout.
- **Bias the loading mixture ratio** so the expected dispersion strands the cheaper propellant.
- **Check the turbomachinery operating range.** On a pump-fed engine it often sets the floor.

---

## Failure modes

**Injector stiffness specified at full thrust on a throttling engine.** It is a fifth of that at 20 per cent throttle, and chug is the result.

**Throttling an engine expanded to the sea level separation limit.** It separates immediately, and the side load is the problem.

**Assuming mixture ratio holds through a throttle.** The two circuits do not scale identically and nothing enforces it.

**Assuming cooling gets easier on throttle-down.** Coolant flow falls with the heat load and the wall can get hotter.

**Loading at the design mixture ratio with no bias.** Symmetric dispersion, asymmetric penalty, and the expensive direction is the more likely one on a fuel-rich-biased engine.

**Treating residuals as a small correction.** Three and a half per cent of propellant is payload-scale.

---

## Worked numbers

Injector authority, 20 per cent stiffness at full thrust:

| Throttle | Stiffness | Note |
|---|---|---|
| 100 % | 20.0 % | Design point |
| 50 % | 10.0 % | Comfortable |
| 40 % | 8.0 % | Conservative floor |
| 25 % | 5.0 % | Aggressive floor |
| 20 % | 4.0 % | Chug territory |

Nozzle separation, area ratio 20.35 at sea level, exit pressure ratio 0.00434:

| Throttle | `Pe` [kPa] | `Pe/Pa` | Separated |
|---|---|---|---|
| 100 % | 43.37 | 0.428 | No |
| 80 % | 34.70 | 0.342 | Yes |
| 50 % | 21.69 | 0.214 | Yes |
| 30 % | 13.01 | 0.128 | Yes |

Residuals for LOX/RP-1 loaded at `MR` 2.56:

| `MR` error | Residual |
|---|---|
| -5 % | 3.60 % |
| -2 % | 1.44 % |
| +2 % | 0.55 % |
| +5 % | 1.34 % |

---

## Standards

| Standard | What it gives you |
|---|---|
| NASA SP-8089 | Liquid rocket engine injectors |
| NASA SP-8113 | Liquid rocket engine combustion stabilization devices |
| NASA SP-8087 | Fluid-cooled combustion chambers, for the throttled cooling case |
| CPIA 655 | Combustion stability testing and rating |
| NASA SP-194 | Liquid propellant rocket combustion instability, the standing reference |

---

## Tool interface

Throttle behaviour is a chamber pressure sweep at fixed geometry, which the performance class supports directly.

```python
from EnginePerformance import EnginePerformance

for throttle in (1.0, 0.8, 0.6, 0.4):

    performance = EnginePerformance()
    performance.setInputs({'combination':     'LOX/RP-1',
                           'chamberPressure': 10.0e6 * throttle,
                           'areaRatio':       20.35})

    result = performance.calculateThrustCoefficient(101325.0)

    print(f'{throttle:.0%} {result["exitPressure"] / 1000.0:6.2f} kPa '
          f'separated {result["separated"]}')
```

Injector stiffness and propellant utilisation are not in the hub library. Injector design belongs in [combustionDevices](../combustionDevices/README.md) and the feed system side belongs in [fluidSystems](../../fluidSystems/README.md).

---

## References

- Harrje and Reardon, NASA SP-194, *Liquid Propellant Rocket Combustion Instability*
- NASA SP-8089, *Liquid rocket engine injectors*
- Dressler, *Summary of Deep Throttling Rocket Engines with Emphasis on Apollo LMDE*
- Casiano, Hulka and Yang, *Liquid-Propellant Rocket Engine Throttling: A Comprehensive Review*
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
