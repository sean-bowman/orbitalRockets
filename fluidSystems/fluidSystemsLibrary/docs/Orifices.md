[Home](../../README.md) > Orifices

# Orifices

## Contents

- [Overview](#overview)
- [Governing physics](#governing-physics)
  - [Incompressible liquid flow](#incompressible-liquid-flow)
  - [The discharge coefficient](#the-discharge-coefficient)
  - [Compressible gas flow](#compressible-gas-flow)
  - [Cavitating and flashing flow](#cavitating-and-flashing-flow)
  - [Two-phase and flashing inlet flow](#two-phase-and-flashing-inlet-flow)
- [Metering orifices: ISO 5167](#metering-orifices-iso-5167)
- [Design procedure](#design-procedure)
- [Design rules of thumb](#design-rules-of-thumb)
- [Manufacturing and hardware](#manufacturing-and-hardware)
- [Failure modes](#failure-modes)
- [Operations](#operations)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

An orifice is a deliberate, fixed restriction in a flow path. It is the most common component in any propulsion fluid system and it appears in at least five distinct roles:

| Role | What it does | Sizing driver |
|---|---|---|
| Injector element | Meters propellant into a combustion or decomposition chamber and sets the atomization | Chamber pressure, injector stiffness, spray quality |
| Trim orifice | Balances parallel branches so each gets its intended share | Flow split, available dP budget |
| Purge restrictor | Limits gas consumption from a bottle or facility supply | Bottle capacity, purge duration |
| Cavitating venturi throat | Decouples upstream flow from downstream pressure | Flow rate, unchoke margin |
| Metering orifice plate | Measures flow by differential pressure | Measurement uncertainty, permanent pressure loss |

The physics is the same in all five cases: a flow area small enough that the fluid accelerates, converts static pressure into velocity head, and dissipates most or all of it downstream. What differs is which part of that process you care about.

The one thing that unites every orifice problem is that the flow rate is set by an area you can measure and a discharge coefficient you usually cannot. Getting the area right is trivial. Getting the discharge coefficient right is the entire engineering problem, and it is why every propulsion organization flow-tests its injectors instead of trusting a calculation.

---

## Governing physics

### Incompressible liquid flow

Apply Bernoulli between a stagnant upstream condition and the vena contracta, assume the pressure at the vena contracta equals the downstream static pressure, and the result is:

```
V_ideal = sqrt( 2 * dP / rho )

mdot = Cd * A * sqrt( 2 * rho * dP )
```

where `A` is the geometric bore area and `Cd` is the discharge coefficient, which lumps together two separate effects:

- **Contraction.** The jet continues to converge downstream of the sharp edge, reaching a minimum area (the vena contracta) smaller than the hole. The contraction coefficient `Cc = A_vc / A` is about 0.61 for a sharp-edged hole discharging into a large volume, and it is a purely geometric consequence of the streamline curvature at the edge.
- **Velocity loss.** Viscous dissipation makes the actual velocity slightly below the ideal. The velocity coefficient `Cv_orifice` is typically 0.97 to 0.99.

`Cd = Cc * Cv_orifice`. For a sharp-edged orifice, `0.61 * 0.98 = 0.60`, which is why the number 0.61 is burned into everyone's memory.

If the orifice sits in a pipe rather than discharging into a plenum, the upstream velocity is not negligible and a velocity-of-approach factor applies:

```
E = 1 / sqrt(1 - beta^4)          beta = d / D
```

At `beta = 0.5` this is 1.033, a 3 percent correction. At `beta = 0.75` it is 1.19, which is not optional.

**Pressure drop form.** Rearranged for the pressure drop at a known flow:

```
dP = mdot^2 / ( 2 * rho * Cd^2 * A^2 )
```

Note the exponents. Pressure drop scales with the square of mass flow and the inverse fourth power of diameter. A 5 percent diameter error is a 22 percent pressure drop error, which is exactly why injector orifice tolerances are held so tight.

### The discharge coefficient

The discharge coefficient is a function of inlet geometry, length-to-diameter ratio, Reynolds number, and surface condition, roughly in that order of importance.

**Inlet geometry and L/D.** These dominate. The values below are the high-Reynolds asymptotes used by the [`Orifice`](../Orifice.py) class:

| Geometry | L/D | Cd | Physical mechanism |
|---|---|---|---|
| Reentrant (Borda) | any | 0.52 | Tube projects into the upstream volume; the flow must turn 180 degrees, maximizing contraction |
| Sharp-edged plate | ~0 | 0.61 | Classical vena contracta, no reattachment |
| Short tube | 0.5 | 0.72 | Flow separates at the inlet but the bore is too short for reliable reattachment. **Unstable** |
| Square-edged bore | 2 to 6 | 0.81 | Flow separates, then reattaches inside the bore, recovering part of the contraction |
| Conical inlet, 30 to 60 deg | 2 to 6 | 0.90 | Gradual convergence largely eliminates separation |
| Rounded inlet, r/d >= 0.25 | 2 to 6 | 0.96 | No separation at all; only friction remains |

The jump from 0.61 to 0.81 between a plate and a drilled bore is a 33 percent flow change from a detail that does not appear on a schematic and is easy to leave off a drawing. **Specify the inlet condition and the L/D on the drawing.** If the print says "0.062 dia thru" and nothing else, the machinist decides your flow rate.

The `L/D = 0.5` short-tube case deserves a specific warning. In that range the separated shear layer sometimes reattaches and sometimes does not, and it can switch between the two states during operation. The result is a bistable Cd that jumps by 15 percent with no change in operating conditions. Design out of that band: either go below `L/D = 0.2` (a true plate) or above `L/D = 2` (a true bore).

**Reynolds number.** Above about `Re = 10^4` the discharge coefficient is essentially constant. Below that it falls, and below `Re = 100` it collapses as the flow becomes viscous-dominated. The normalized curve used by the class is:

| Re | Cd / Cd_inf |
|---|---|
| 10 | 0.11 |
| 100 | 0.37 |
| 300 | 0.62 |
| 1 000 | 0.84 |
| 3 000 | 0.94 |
| 10 000 | 0.99 |
| >= 30 000 | 1.00 |

This matters more often than people expect. A small trim orifice passing a cold, viscous propellant at a low flow rate can easily sit at `Re = 2000`, where `Cd` is 10 percent below the catalog value. Bore Reynolds number is

```
Re_d = rho * V * d / mu = (4 * mdot) / (pi * d * mu)
```

Note that at fixed mass flow, `Re_d` scales as `1/d`: **smaller orifices have higher Reynolds numbers**, not lower. Low-Re problems come from low flow, high viscosity, or many parallel elements splitting the flow, not from small holes as such.

**Surface condition.** Second-order for a machined hole. It matters for additively manufactured passages, where an as-built `Ra` of 10 to 20 microns in a 1 mm bore is a relative roughness of 1 to 2 percent, enough to shift `Cd` by several percent and, worse, enough to vary part to part.

### Compressible gas flow

For a gas, the density changes through the orifice and the incompressible relation fails. Two regimes exist, separated by the critical pressure ratio.

**Critical pressure ratio.** The flow chokes (reaches Mach 1 at the throat) when

```
P2 / P1 <= ( 2 / (gamma + 1) )^( gamma / (gamma - 1) )
```

| Gas | gamma | Critical ratio |
|---|---|---|
| Helium, argon (monatomic) | 1.667 | 0.487 |
| Nitrogen, oxygen, air, hydrogen (diatomic) | 1.40 | 0.528 |
| Methane | 1.31 | 0.544 |
| Hot gas, hydrazine products | 1.25 to 1.30 | 0.549 to 0.545 |

The number to keep in your head is **0.528 for diatomic gases**. Any GN2 or GHe line venting to atmosphere from more than about 2 atm absolute upstream is choked.

**Choked flow.**

```
mdot = Cd * A * P1 * sqrt( gamma / (R * T1) ) * ( 2 / (gamma + 1) )^( (gamma+1) / (2*(gamma-1)) )
```

with `R` the specific gas constant `R_universal / M`. Once choked, the mass flow depends **only** on upstream stagnation conditions. Downstream pressure has no effect whatsoever. That property is what makes a choked orifice such a useful component: a purge restrictor gives constant, predictable gas consumption regardless of what the downstream plumbing is doing, and a choked orifice upstream of a thruster isolates the feed system from chamber pressure oscillations.

Two second-order effects are worth knowing:

- **Temperature sensitivity.** `mdot` scales as `1/sqrt(T1)`. A purge restrictor sized at 293 K passes 8 percent more gas at 250 K. Cold-day margins are not free.
- **Upstream stagnation, not static.** `P1` and `T1` in the equation are stagnation values. If the approach velocity is significant (a small orifice in a small line at high flow) the static-to-stagnation difference matters.

**Subsonic compressible flow.**

```
mdot = Cd * A * P1 * sqrt( (2*gamma) / ((gamma-1) * R * T1) * ( r^(2/gamma) - r^((gamma+1)/gamma) ) )
```

with `r = P2 / P1`. This reduces to the incompressible form as `r` approaches 1 and matches the choked expression exactly at the critical ratio, so no branch discontinuity exists.

### Cavitating and flashing flow

For a liquid, the static pressure at the vena contracta is lower than the downstream pressure, because the flow has not yet decelerated and recovered. If the vena contracta pressure reaches the fluid vapor pressure, vapor forms.

Once that happens, the throat pressure is pinned at `P_vapor` and the effective driving head becomes `(P1 - P_vapor)` instead of `(P1 - P2)`:

```
mdot = Cd * A * sqrt( 2 * rho * (P1 - P_vapor) )
```

Further reduction in downstream pressure buys nothing. The orifice has choked on vapor pressure.

The severity is characterized by a cavitation index. The [`Orifice`](../Orifice.py) class uses

```
sigma = (P2 - P_vapor) / (P1 - P2)
```

| sigma | Status | What happens |
|---|---|---|
| > 1.8 | None | No vapor anywhere |
| 0.6 to 1.8 | Incipient | Audible, intermittent vapor pockets, minor erosion |
| < 0.6 | Developed | Continuous cavity, noise, erosion, flow no longer follows the dP relation |
| P2 <= P_vapor | Flashing | Two-phase downstream; the fluid does not recondense |

The distinction between **cavitating** and **flashing** matters operationally. In cavitation, the bubbles collapse when the flow recovers pressure downstream, and each collapse is a microjet impact on whatever surface is nearby. That is what destroys hardware. In flashing, the downstream pressure never recovers above vapor pressure, the bubbles never collapse, and the damage mechanism is erosion by a high-velocity two-phase jet rather than implosion. Cavitation is fixed by staging the pressure drop or moving the collapse away from a wall; flashing is fixed by raising the downstream pressure or accepting hardened material.

### Two-phase and flashing inlet flow

If the fluid arrives already saturated or two-phase (a cryogen at its boiling point, or a propellant that has been sitting in a sun-warmed line), neither the liquid nor the gas relation applies. Two methods are standard:

**Homogeneous Equilibrium Model (HEM).** Assumes the liquid and vapor are in thermal and mechanical equilibrium and move at the same velocity. Integrate along an isentrope from the stagnation state and find the mass flux maximum. HEM is accurate for long passages (`L/D > 10`) where equilibrium has time to establish, and it under-predicts flow for short passages where the liquid does not have time to flash.

**Omega method (Leung).** A closed-form approximation to HEM that parameterizes the two-phase compressibility with a single number:

```
omega = ( x0 * v_fg / v0 ) + ( C_pl * T0 * P0 / v0 ) * ( v_fg / h_fg )^2
```

The first term is the flashing contribution of the existing vapor fraction `x0`; the second is the contribution of vapor generated by depressurization. For a saturated liquid inlet (`x0 = 0`) the first term vanishes. The critical pressure ratio and critical mass flux then follow from `omega` alone, which makes the method very usable for relief device sizing.

**Practical guidance.** For an orifice shorter than about `L/D = 3` passing a marginally subcooled liquid, the flow is closer to the pure liquid ("frozen") value than to HEM, because there is not enough residence time to nucleate. That is a favorable error for safety but an unfavorable one for flow accuracy. If your propellant can arrive saturated, either subcool it enough that it cannot, or test it.

---

## Metering orifices: ISO 5167

When the orifice is a flow measurement device rather than a flow control device, the discharge coefficient must be known without calibration. That is what ISO 5167 provides: a rigidly specified plate geometry, tapping arrangement, and installation, with an empirical `C` equation good to about 0.5 percent.

**The Reader-Harris/Gallagher equation** (ISO 5167-2):

```
C = 0.5961 + 0.0261*beta^2 - 0.216*beta^8
    + 0.000521*(1e6*beta/Re_D)^0.7
    + (0.0188 + 0.0063*A) * beta^3.5 * (1e6/Re_D)^0.3
    + (0.043 + 0.080*exp(-10*L1) - 0.123*exp(-7*L1)) * (1 - 0.11*A) * beta^4/(1-beta^4)
    - 0.031*(M2' - 0.8*M2'^1.1) * beta^1.3
```

with `A = (19000*beta/Re_D)^0.8` and `M2' = 2*L2'/(1-beta)`. For pipes below 71.12 mm add `0.011*(0.75 - beta)*(2.8 - D/25.4)` with `D` in mm.

`L1` and `L2'` are the upstream and downstream tapping distances normalized by pipe diameter:

| Tapping | L1 | L2' |
|---|---|---|
| Corner | 0 | 0 |
| Flange | 25.4 / D_mm | 25.4 / D_mm |
| D and D/2 | 1 | 0.47 |

**Expansibility factor** for compressible flow:

```
epsilon = 1 - (0.351 + 0.256*beta^4 + 0.93*beta^8) * ( 1 - (P2/P1)^(1/kappa) )
```

**Validity limits.** `0.10 <= beta <= 0.75`, `50 mm <= D <= 1000 mm`, `Re_D >= 5000`. Outside those bounds the equation still evaluates but the uncertainty claim does not hold. Small-bore aerospace tubing is usually below the diameter limit, which is why aerospace flow measurement leans on Coriolis, turbine and venturi meters rather than plates.

**Permanent pressure loss.** A plate recovers part of its differential downstream of the vena contracta:

```
dP_permanent / dP_measured = 1 - beta^1.9
```

At `beta = 0.5` you keep 27 percent and lose 73 percent. At `beta = 0.75` you lose 42 percent. That loss is the price of the measurement, and it is why a venturi (5 to 20 percent loss) is preferred where pressure budget is tight.

**Straight run requirements.** ISO 5167 specifies minimum upstream and downstream straight lengths that depend on `beta` and on what the upstream disturbance is: typically 10 to 44 diameters upstream, 4 to 8 downstream. Violating them is the single most common cause of a metering orifice reading wrong, and no amount of correlation refinement fixes a swirling inlet profile.

---

## Design procedure

**1. Establish the duty.** Required mass flow, fluid, upstream temperature, and the pressure differential available. Be explicit about whether the differential is a budget allocation you must hit or a maximum you must not exceed.

**2. Decide the role.** Flow control (`injector` model), flow measurement (`plate` model), or flow decoupling (a cavitating venturi, which has its own class). The role determines the geometry class and the acceptable Cd uncertainty.

**3. Check the regime before sizing.**
   - Liquid: compare `P2` against the vapor pressure at `T1`. If `P2` is within a factor of two of `P_vapor`, expect cavitation and design for it.
   - Gas: compute `P2/P1` and compare against the critical ratio. If the orifice will be choked, size on the choked relation and note that the downstream pressure is now irrelevant.

**4. Pick the geometry and the Cd.** Choose the inlet condition and `L/D` deliberately. Use the table above. Avoid `L/D` between 0.2 and 2.

**5. Size the area.**
```
A = mdot / ( Cd * sqrt(2 * rho * dP) )              incompressible
A = mdot / ( Cd * G_choked )                        choked gas
```

**6. Check Reynolds number** at the resulting diameter and re-evaluate `Cd`. Iterate. The [`Orifice`](../Orifice.py) class does this automatically.

**7. Snap to a real hole size.** Orifices are made with drills, and a drill index is discrete. Take the sizes above and below and compute the flow error each gives. Choose deliberately, and put the resulting flow tolerance in the requirement, not the diameter tolerance.

**8. Set the tolerance.** Because `mdot` scales with `d^2`, a diameter tolerance of `+/- x` percent gives a flow tolerance of `+/- 2x` percent. A typical injector orifice at 1 mm diameter with a `+/- 0.013 mm` (0.0005 in) tolerance is `+/- 1.3` percent on diameter and `+/- 2.6` percent on flow before any `Cd` variation is counted.

**9. Decide whether to flow-test.** If flow accuracy better than 5 percent matters, flow-test. There is no correlation that beats a calibration.

---

## Design rules of thumb

| Rule | Value | Why |
|---|---|---|
| Injector stiffness | `dP_injector / P_chamber` = 0.15 to 0.25 | Below about 0.10 the chamber can drive the feed system and couple into combustion instability. Above 0.30 the pressure budget cost is not buying anything |
| Monopropellant injector stiffness | 0.20 to 0.30 | Catalyst beds have their own pressure oscillations; more isolation is warranted |
| Avoid the bistable band | `L/D` outside 0.2 to 2 | Flow reattachment is not repeatable in that band |
| Minimum practical bore | ~0.25 mm (0.010 in) | Below this, contamination reliably plugs it and drilling accuracy degrades |
| Filtration ahead of an orifice | Absolute rating <= d/10 | A particle larger than a tenth of the bore will eventually lodge |
| Sharp-edge preservation | Edge radius <= 0.02 d | A radius of 5 percent of the diameter raises `Cd` measurably; deburring an orifice changes its flow |
| Flow tolerance from diameter tolerance | 2x the diameter tolerance | `mdot ~ d^2` |
| Choked orifice temperature sensitivity | -0.5 percent flow per +1 percent T | `mdot ~ 1/sqrt(T)` |
| Cavitation margin for a non-cavitating orifice | `sigma > 2` | Keeps the vena contracta clear of vapor pressure with margin for temperature rise |
| Parallel elements | Prefer N smaller over 1 larger for atomization, 1 larger for cleanliness robustness | Direct trade; N elements each pass 1/N of the flow, so each sees a lower Reynolds number |

---

## Manufacturing and hardware

**Drilling.** The default. Cheap, fast, and the `Cd` is set by the drill geometry and the entry condition. A drilled hole has a burr on both ends. The exit burr is harmless; the **entry burr is not**, because it sits exactly where the contraction happens. Specify how it is to be removed (hand-deburr, abrasive flow, electropolish) and understand that each method changes `Cd` differently.

**EDM.** Electrical discharge machining produces small holes (down to 0.1 mm) with sharp, burr-free edges and a recast layer. Standard for injector faces in hard alloys. The recast layer is brittle and should be removed for fatigue-critical parts.

**Laser drilling.** Fast for many small holes, produces a slight taper (entry larger than exit) and a recast layer. The taper means the flow direction matters: reversed flow through a laser-drilled hole has a different `Cd`.

**Additive manufacturing.** Attractive for integrated manifolds with many internal orifices, but as-built internal surfaces are rough (`Ra` 10 to 20 microns) and small features come out undersized relative to nominal because of partially sintered powder adhesion. Below about 0.8 mm, LPBF passages are not dimensionally trustworthy without post-machining or abrasive flow. **Always** flow-test additively manufactured orifices; do not trust the CAD dimension.

**Orifice plates and cartridges.** A replaceable orifice cartridge (a small plate captured in a fitting or a union) is worth its complexity on a development program: it lets flow be re-trimmed without rebuilding the manifold. Lee Company restrictors and similar commercial products come with a calibrated flow rating in Lohms, which is a flow resistance unit defined so that 1 Lohm passes 100 gpm of water at 25 psid; a higher Lohm rating means less flow.

---

## Failure modes

**Contamination plugging.** By far the most common. A single particle larger than roughly a third of the bore will lodge and stay. The consequences scale with what the orifice was doing: a plugged trim orifice starves one branch, a plugged injector element creates a local mixture ratio excursion, and a plugged purge restrictor removes the purge without any indication. Mitigate with an absolute-rated filter immediately upstream, sized at or below `d/10`, and with cleanliness control through assembly.

**Erosion.** The bore grows, `Cd` rises, and flow increases over time. Driven by cavitation, two-phase flow, or entrained particulate. Detectable by trending flow rate at constant differential across a test series. If an injector's flow number climbs run over run, you are eroding.

**Edge rounding.** Slower than erosion and less obvious. A sharp edge that rounds to `r/d = 0.05` gains several percent in `Cd`. The flow rises with no visible damage.

**Cavitation damage downstream.** The orifice itself often survives; the damage appears 5 to 20 diameters downstream where the cavity collapses. If you find pitting on a downstream elbow and cannot explain it, look at the upstream restriction.

**Flow direction reversal.** An orifice is not symmetric unless it is a true thin plate. A tapered, counterbored or laser-drilled hole has a different `Cd` in each direction, sometimes by 20 percent. Mark flow direction on the part.

**Adiabatic compression at a restriction.** In a GOX or LOX system, rapidly pressurizing against a closed valve compresses the trapped gas downstream of an orifice and heats it. Compressing GOX from 1 to 20 MPa adiabatically takes it from 293 K to about 690 K, and from 1 atm to 20 MPa takes it to about 1330 K, both of which are above the autoignition temperature of most non-metals. This is a real ignition mechanism, and it is a reason to open oxygen valves slowly and to keep polymers out of dead-ended oxygen volumes.

**Whistling and acoustic coupling.** A choked orifice generates broadband noise, and a resonant downstream cavity can turn that into a tone with enough energy to fatigue thin-wall tubing. It is uncommon, but when it happens it fails hardware quickly.

---

## Operations

**Acceptance flow testing.** Flow the element with a reference fluid (usually water or IPA for liquid elements, GN2 for gas) at a defined differential, and record the flow number:

```
K_w = mdot / sqrt(dP)          [kg/s / sqrt(Pa)]
```

Report it as a flow number rather than a `Cd`, because the flow number is a directly measured quantity and the `Cd` requires assuming an area. Convert between reference fluid and service fluid by density ratio, and note that the conversion is only valid if the Reynolds numbers are comparable.

**Bore inspection.** Pin gages verify diameter but not edge condition, and edge condition is what sets `Cd`. Borescope or optical comparator inspection of the entry edge is worth the effort on flight injectors.

**Trending.** Log the flow number for every element across every test. The trend is the fastest diagnostic you have for erosion, plugging and edge rounding, and it costs nothing once the data is being recorded anyway.

**Cleanliness.** Blow-down and flush before installing anything upstream of a small orifice, and verify filter integrity after any system disturbance. The most expensive orifice failure is the one caused by a particle that came off the inside of a line you opened last week.

---

## Worked example

A hydrazine monopropellant thruster requires 0.045 kg/s at a 0.30 MPa injector differential, at 293.15 K, through a single square-edged bore with `L/D = 3`.

**Fluid properties** (from [`utils.hydrazineProps`](../utils.py)):

| Property | Value |
|---|---|
| Density | 1008.5 kg/m^3 |
| Dynamic viscosity | 9.74e-4 Pa-s |
| Vapor pressure | 1.43 kPa |

**Sizing.** With `Cd = 0.81`:

```
A = 0.045 / ( 0.81 * sqrt(2 * 1008.5 * 3.0e5) ) = 2.258e-6 m^2
d = 1.696 mm
```

**Reynolds check.** `V = 19.76 m/s`, `Re = 1008.5 * 19.76 * 0.001696 / 9.74e-4 = 3.47e4`, which is above 10^4, so the asymptotic `Cd` stands and no correction is needed.

**Cavitation check.** `sigma = (1.90e6 - 1.43e3) / 3.0e5 = 6.33`, well clear of the incipient threshold of 1.8. No cavitation.

**Drill selection.**

| Drill | Diameter | Mass flow | Error |
|---|---|---|---|
| No. 52 | 1.6129 mm (0.0635 in) | 0.04071 kg/s | -9.5 % |
| No. 51 | 1.7018 mm (0.0670 in) | 0.04532 kg/s | +0.7 % |

The No. 51 drill is the obvious choice at +0.7 percent. Note how coarse the drill index is at this diameter: one size step is a 10 percent flow change. If the flow tolerance were tighter than +/- 5 percent, this element would need to be reamed to size or EDM'd rather than drilled.

Reproduce with:

```python
from Orifice import Orifice

element = Orifice()
element.setInputs({'fluid': 'N2H4', 'upstreamPressure': 2.20e6,
                   'downstreamPressure': 1.90e6, 'upstreamTemperature': 293.15,
                   'massFlow': 0.045, 'orificeType': 'square'})
element.sizeDiameter()
print(element.generateReport())
```

---

## Standards

| Standard | Scope |
|---|---|
| ISO 5167-1 | Measurement of fluid flow by pressure differential devices, general principles |
| ISO 5167-2 | Orifice plates: geometry, tappings, discharge coefficient, installation |
| ISO 5167-4 | Venturi tubes |
| ASME MFC-3M | Measurement of fluid flow in pipes using orifice, nozzle and venturi |
| ASME PTC 19.5 | Flow measurement instruments and apparatus |
| ISA RP3.2 | Flow measurement practice |
| NASA SP-8089 | Liquid rocket engine injectors (design criteria monograph) |
| NASA SP-8080 | Liquid rocket pressure regulators, relief valves, check valves, burst disks and explosive valves |

---

## Tool interface

The [`Orifice`](../Orifice.py) class implements everything above.

```python
from Orifice import Orifice

# Sizing: find the diameter for a required flow
element = Orifice()
element.setInputs({'fluid': 'N2H4', 'upstreamPressure': 2.20e6,
                   'downstreamPressure': 1.90e6, 'upstreamTemperature': 293.15,
                   'massFlow': 0.045, 'orificeType': 'square'})
element.sizeDiameter()

# Analysis: find the flow through a known hole
restrictor = Orifice()
restrictor.setInputs({'fluid': 'Nitrogen', 'upstreamPressure': 5.0e6,
                      'downstreamPressure': 101325.0, 'upstreamTemperature': 293.15,
                      'diameter': 0.001, 'orificeType': 'sharp'})
restrictor.calculateMassFlow()      # returns the choked value
print(restrictor.regime)            # 'choked gas'

# Metering: ISO 5167-2 plate
meter = Orifice()
meter.setInputs({'fluid': 'Water', 'upstreamPressure': 1.0e6,
                 'downstreamPressure': 0.98e6, 'upstreamTemperature': 293.15,
                 'diameter': 0.05, 'pipeDiameter': 0.10,
                 'model': 'plate', 'tappings': 'flange'})
meter.calculateMassFlow()
print(meter.dischargeCoefficient)          # Reader-Harris/Gallagher value
print(meter.permanentPressureLoss)         # unrecovered loss
```

Key attributes after a solve: `diameter`, `area`, `dischargeCoefficient`, `massFlow`, `velocity`, `reynolds`, `regime`, `isChoked`, `cavitationNumber`, `cavitationStatus`, `permanentPressureLoss`.

`generateReport()` prints the full state plus the nearest standard drill sizes and the flow error each would give.

---

## References

1. ISO 5167-2:2022, *Measurement of fluid flow by means of pressure differential devices inserted in circular cross-section conduits running full -- Part 2: Orifice plates*.
2. Reader-Harris, M. J. and Sattary, J. A., "The Orifice Plate Discharge Coefficient Equation", *Flow Measurement and Instrumentation*, Vol. 1, 1990.
3. Lichtarowicz, A., Duggins, R. K. and Markland, E., "Discharge Coefficients for Incompressible Non-Cavitating Flow through Long Orifices", *Journal of Mechanical Engineering Science*, Vol. 7, No. 2, 1965.
4. Crane Co., *Flow of Fluids Through Valves, Fittings, and Pipe*, Technical Paper No. 410.
5. Leung, J. C., "A Generalized Correlation for One-Component Homogeneous Equilibrium Flashing Choked Flow", *AIChE Journal*, Vol. 32, No. 10, 1986.
6. NASA SP-8089, *Liquid Rocket Engine Injectors*, 1976.
7. Huzel, D. K. and Huang, D. H., *Modern Engineering for Design of Liquid-Propellant Rocket Engines*, AIAA Progress in Astronautics and Aeronautics Vol. 147, 1992.
8. Idelchik, I. E., *Handbook of Hydraulic Resistance*, 4th ed., Begell House, 2007.
