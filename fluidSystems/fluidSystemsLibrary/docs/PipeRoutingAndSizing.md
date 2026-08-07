[Home](../../README.md) > Pipe Routing and Sizing

# Pipe Routing and Sizing

## Contents

- [Overview](#overview)
- [Governing physics](#governing-physics)
  - [Darcy-Weisbach and the friction factor](#darcy-weisbach-and-the-friction-factor)
  - [Surface roughness](#surface-roughness)
  - [Minor losses](#minor-losses)
  - [Compressible flow in lines](#compressible-flow-in-lines)
  - [Elevation and acceleration terms](#elevation-and-acceleration-terms)
- [Sizing procedure](#sizing-procedure)
- [Velocity limits](#velocity-limits)
- [Wall thickness and pressure design](#wall-thickness-and-pressure-design)
- [Routing](#routing)
- [Supports and dynamics](#supports-and-dynamics)
- [Thermal growth and contraction](#thermal-growth-and-contraction)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Operations](#operations)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Line sizing is where the pressure budget is spent and where vehicle mass is quietly created. The chain runs in one direction and it is worth internalizing:

```
line diameter  ->  pressure drop  ->  required tank pressure  ->  tank wall thickness  ->  vehicle mass
```

Undersizing a feed line by one tube size can cost more mass in tank wall than the entire valve complement weighs. Oversizing costs line mass, propellant residuals in the line, and chilldown mass on a cryogenic system. The right answer is a considered trade, not a default.

Routing is the other half of the problem and it is usually harder, because it is constrained by things that have nothing to do with fluid mechanics: where the structure is, where the harness runs, what has to be removable for maintenance, and what happens when the whole assembly shrinks by a centimeter at cryogenic temperature.

---

## Governing physics

### Darcy-Weisbach and the friction factor

```
dP_friction = f * (L / D) * (rho * V^2) / 2
```

`f` here is the **Darcy** friction factor. The **Fanning** friction factor is one quarter of it. Half of all published pressure drop discrepancies trace to that factor of four. This library uses Darcy everywhere and says so at every call site.

In terms of mass flow, which is what a feed system model actually carries:

```
dP_friction = f * (L / D) * ( mdot^2 / (2 * rho * A^2) )
            = 8 * f * L * mdot^2 / ( pi^2 * rho * D^5 )
```

**`dP` scales as `D^-5`.** This is the single most important sensitivity in a fluid system model. A 10 percent error in inner diameter is a 61 percent error in pressure drop. It is why you use the actual ID of the actual tube, not the nominal size, and why a tube ID tolerance matters.

**Reynolds number:**

```
Re = rho * V * D / mu = 4 * mdot / (pi * D * mu)
```

**Friction factor correlations:**

| Regime | Correlation | Notes |
|---|---|---|
| Laminar, `Re < 2300` | `f = 64 / Re` | Exact for fully developed flow in a circular pipe |
| Transition, `2300 < Re < 4000` | Not well defined | See below |
| Turbulent | Colebrook-White (implicit) | The reference; the basis of the Moody diagram |
| Turbulent | Haaland (explicit) | Within 2 percent of Colebrook, cheap |
| All regimes | Churchill (1977) | Single expression, no branching, ~1 percent of Colebrook when turbulent |

**Colebrook-White:**

```
1/sqrt(f) = -2 * log10( eps/(3.7*D) + 2.51/(Re*sqrt(f)) )
```

**Haaland:**

```
1/sqrt(f) = -1.8 * log10( (eps/(3.7*D))^1.11 + 6.9/Re )
```

**Churchill:**

```
f = 8 * [ (8/Re)^12 + 1/(A + B)^1.5 ]^(1/12)
A = [ -2.457 * ln( (7/Re)^0.9 + 0.27*eps/D ) ]^16
B = ( 37530 / Re )^16
```

Churchill is the default in [`utils.frictionFactor`](../utils.py) because it does not branch. Any solver that might march a line through the transition region will produce a discontinuous derivative with a branched correlation, and discontinuous derivatives break secant and Newton solvers.

**The transition region is not a correlation problem, it is a physics problem.** Between `Re = 2300` and `Re = 4000` the friction factor is not a well-defined function of Reynolds number: it depends on inlet disturbance, vibration, and history. Any smooth curve through it is an interpolation, not a prediction. Size hardware so the operating point is not in that band, and if it must be, carry the uncertainty explicitly rather than pretending the correlation is accurate.

### Surface roughness

Roughness enters only through `eps/D`, so it matters enormously in small-bore tubing and barely at all in a large duct.

| Surface | eps [micron] | eps/D at 6 mm ID |
|---|---|---|
| Glass, drawn plastic | 0 | 0 |
| **Drawn stainless/copper/aluminum tube** | **1.5** | **2.5e-4** |
| Commercial stainless pipe | 15 | 2.5e-3 |
| Commercial steel pipe | 45 | 7.5e-3 |
| Galvanized steel | 150 | 2.5e-2 |
| Convoluted metal flex hose | 300 | 5.0e-2 |
| Braided flex hose | 500 | 8.3e-2 |
| **LPBF as-built, upskin** | **20** | **3.3e-3** |
| **LPBF as-built, downskin** | **40** | **6.7e-3** |
| LPBF after abrasive flow machining | 5 | 8.3e-4 |
| DED as-built | 100 | 1.7e-2 |

Two entries deserve emphasis.

**Flex hose.** A convoluted metal hose is not a smooth tube with a slightly higher roughness. The convolutions are a series of sudden expansions and contractions, and the loss is better modeled as an added `K` per unit length (roughly 0.6 per meter) on top of a nominal friction term. A meter of flex hose can easily cost as much pressure as five meters of straight tube.

**Additive manufacturing.** As-built LPBF internal surfaces are one to two orders of magnitude rougher than drawn tube, and downskin (overhanging) surfaces are worse than upskin because of partially sintered powder adhesion. An additively manufactured manifold sized on drawn-tube roughness will under-predict its pressure drop by a large factor. If you cannot post-process the internal passages, size them on the as-built number and verify by flow test.

### Minor losses

Every bend, tee, contraction, expansion, valve and fitting adds a loss. Two equivalent formulations are in common use.

**K-factor method:**

```
dP_minor = K * rho * V^2 / 2
```

**Equivalent length method:**

```
L_eq = (L/D)_fitting * D          added to the physical length
```

The two agree exactly in fully turbulent flow (where `K = f_T * (L/D)`) and diverge in laminar flow, where the K method is closer to correct. The [`Line`](../Line.py) class supports both.

**Equivalent length ratios** (Crane TP-410):

| Fitting | L/D |
|---|---|
| Bend, r/D = 5 | 10 |
| Bend, r/D = 3 (typical aerospace tube bend) | 12 |
| Elbow, 45 degree | 16 |
| Elbow, 90 degree long radius (r/D = 1.5) | 20 |
| Elbow, 90 degree standard (r/D = 1) | 30 |
| Tee, flow through run | 20 |
| Tee, flow through branch | 60 |
| Return bend, 180 degree | 50 |
| Ball valve, full bore, open | 3 |
| Gate valve, open | 8 |
| Plug valve, open | 18 |
| Butterfly valve, open | 45 |
| Swing check valve | 100 |
| **Globe valve, open** | **340** |
| Lift check valve | 600 |

The globe valve number is not a typo. A fully open globe valve costs as much pressure as 340 diameters of straight pipe. That is why globe valves are throttling devices and never isolation valves, and why a "just put a globe valve there for now" decision on a development stand quietly eats the entire feed system pressure budget.

**K factors for geometry features:**

| Feature | K |
|---|---|
| Entrance, rounded (r/D >= 0.15) | 0.04 |
| Entrance, sharp | 0.50 |
| Entrance, reentrant (Borda) | 0.78 |
| Exit into a large volume | 1.00 |
| Sudden contraction, area ratio `beta = d/D` | `0.5 * (1 - beta^2)` |
| Sudden expansion, area ratio `beta` | `(1 - beta^2)^2` |
| AN/MS 37 degree flared union | 0.20 |
| VCR metal gasket union | 0.15 |
| Quick disconnect | 2.0 (design dependent; measure) |

The exit `K = 1.0` is exact and often forgotten: all of the remaining velocity head is dissipated into the downstream volume. In a short, fast line that term alone can be a significant fraction of the total.

**Bend loss is not just the K factor.** A bend also generates a secondary (Dean) flow that persists for 10 to 50 diameters downstream and raises the friction there. Two bends close together in perpendicular planes are worse than the sum of their individual losses. If a routing has several bends within a few diameters of each other, add margin.

### Compressible flow in lines

For a gas, density falls with pressure along the line. Mass flow is conserved, so velocity rises, and the friction loss per unit length rises with the square of velocity. A lumped calculation using inlet density **always under-predicts** the drop, and the error grows with pressure ratio.

Three treatments, in increasing fidelity:

**1. Incompressible approximation.** Valid when `dP/P1 < 0.10` or `Mach < 0.3`. Use inlet density and accept a few percent error.

**2. Isothermal marching.** Discretize the line, re-evaluate density at each station's local pressure, accumulate. Appropriate when the line is short enough that the wall holds the fluid at ambient temperature, which is the usual case for vehicle plumbing. This is what [`Line.calculatePressureDrop`](../Line.py) does.

The closed-form isothermal result for an ideal gas is:

```
P1^2 - P2^2 = ( G^2 * R * T / A^2 ) * [ f*L/D + 2*ln(P1/P2) ]
```

with `G` the mass flux. The `2*ln(P1/P2)` term is the acceleration contribution.

**3. Fanno line (adiabatic).** Appropriate for a long insulated line or a fast blowdown. The gas cools as it expands and accelerates, and the limiting condition is `Mach = 1` at the exit. The maximum length for a given inlet Mach number is:

```
4*f_Fanning*L_max/D = (1 - M^2)/(gamma*M^2) + (gamma+1)/(2*gamma) * ln[ (gamma+1)*M^2 / (2 + (gamma-1)*M^2) ]
```

**Choking at the exit.** A gas line that reaches `Mach = 1` at its exit cannot pass more flow no matter how low the downstream pressure goes. The [`Line`](../Line.py) class raises `ChokedFlowError` rather than returning a negative pressure, because a silently choked line is a very confusing failure mode in a system model.

### Elevation and acceleration terms

```
dP_elevation   = rho * g * dz
dP_acceleration = G * (V_out - V_in)      G = mass flux
```

Elevation matters for tall ground systems and for dense propellants: a 10 m column of LOX is 112 kPa (16 psi), which is not negligible against a 300 kPa feed pressure. It is irrelevant in flight except during high-g phases, where the effective `g` is the vehicle acceleration and can be several times standard gravity.

The acceleration term is zero for an incompressible liquid at constant area and significant for a gas line with a meaningful pressure ratio.

---

## Sizing procedure

**1. Establish the duty.** Mass flow, fluid, inlet temperature and pressure, developed length, fitting count. Get the developed length right: it is the length along the centerline of the routed path, not the straight-line distance, and it is typically 1.3 to 2 times the latter.

**2. Apply the velocity limit.** This is often the binding constraint and it is always a hard one.

```
D_velocity = sqrt( 4 * mdot / (pi * rho * V_limit) )
```

**3. Apply the pressure drop budget.** Solve iteratively for the diameter that hits the allocated `dP`, including minor losses.

**4. Take the larger of the two.** A line must satisfy both.

**5. Snap up to a standard tube size.** Snapping down blows the pressure budget, and pressure budget overruns propagate all the way back to tank pressure. Snapping up costs a small mass penalty and buys margin. Standard sizes are in [`Line.STANDARD_TUBE_SIZES_IN`](../Line.py).

**6. Verify the wall thickness** at the design pressure for the selected OD, and reject the size if the standard wall is inadequate.

**7. Recompute the pressure drop** with the real geometry. The snapped size will give a lower `dP` than the budget; record the margin.

**8. Check Reynolds number.** If the operating point lands between `Re = 2300` and `4000`, note it and carry uncertainty.

---

## Velocity limits

These are not physics. They are accumulated operational experience, and two of them are hard safety limits rather than guidance.

| Service | Limit [m/s] | Limit [ft/s] | Driver |
|---|---|---|---|
| Liquid, general | 10 | 33 | Minor losses and erosion start to dominate above this |
| Liquid, pump suction | 3 | 10 | NPSH protection; the suction line is where cavitation starts |
| Liquid propellant fill | 5 | 16 | Limits stored kinetic energy, and therefore surge, when a fill valve slams |
| Cryogenic two-phase (chilldown) | 3 | 10 | Keeps slug velocity down; a liquid slug hitting a bend at 20 m/s is a water hammer event |
| Hydrazine | 6 | 20 | Limits adiabatic compression energy on rapid valve closure |
| **LOX, general** | **7.6** | **25** | **Particle impact ignition. NASA guidance** |
| LOX, verified-clean system with no soft goods in the flow path | 12.2 | 40 | Relaxed limit, requires cleanliness verification |
| **GOX, carbon steel** | **30** | **100** | **Particle impingement ignition, ASTM G88 / NASA-STD-6001** |
| Gaseous, general (inert) | 100 | 330 | Noise, erosion, and the incompressible-treatment limit |

**On the oxygen limits.** These exist because a particle entrained in a high-velocity oxygen stream that impacts a wall or a fitting transition converts its kinetic energy into local heating, and in an oxygen environment that can ignite the particle, which then ignites the substrate. The mechanism is real, well documented, and has destroyed hardware and killed people. The velocity limits are a function of pressure and material: at higher pressures and for less ignition-resistant materials the limits are lower. Treat NASA-STD-6001 and ASTM G88 as governing, not as guidance, and note that impingement sites (elbows, tees, valve seats) are where the limit really applies.

**Gas velocity and Mach number.** For gases the more useful limit is often Mach number rather than absolute velocity. Keep `Mach < 0.3` if you want to use incompressible relations, and `Mach < 0.2` if noise matters.

---

## Wall thickness and pressure design

**ASME B31.3 straight pipe:**

```
t = P * D / ( 2 * ( S*E*W + P*Y ) )
```

| Symbol | Meaning | Typical |
|---|---|---|
| `P` | Internal design gauge pressure | MEOP |
| `D` | Outer diameter | |
| `S` | Basic allowable stress at design temperature | See below |
| `E` | Longitudinal weld joint quality factor | 1.00 seamless, 0.85 ERW, 0.80 furnace butt weld |
| `W` | Weld joint strength reduction factor | 1.00 below the creep range |
| `Y` | Table 304.1.1 coefficient | 0.4 for ferritic and austenitic steel below 900 degF |

Then

```
t_min     = t + corrosion/erosion allowance + mechanical allowances
t_ordered = t_min / (1 - mill tolerance)
```

Mill tolerance is 12.5 percent for seamless pipe and typically 10 percent for tube. The mill is allowed to ship you a wall that thin, so you must order thick enough that the thin end of the tolerance still passes.

**Basic allowable stress.** B31.3 sets `S` as the lesser of two-thirds of yield and one-third of ultimate at temperature. Pressure vessel Section VIII Division 1 uses a 3.5 divisor on ultimate. [`utils.materialProperties`](../utils.py) uses the more conservative `min(2/3 * yield, ultimate / 3.5)`, because flight hardware rarely gets to use the thinner option.

**What B31.3 does not cover.** Pressure design thickness is a hoop stress check only. It says nothing about:

- External pressure (vacuum jacket collapse, which is a buckling problem, not a stress problem)
- Bending from thermal growth or from support spacing
- Fatigue from pressure and thermal cycling
- Handling and installation loads, which usually set the minimum wall on small-bore tubing
- Vibration

On a flight vehicle, **AIAA S-080** (metallic pressure vessels) and **AIAA S-081** (composite overwrapped pressure vessels) factors of safety generally govern instead, with proof and burst factors applied to MEOP:

| Class | Proof factor | Burst factor |
|---|---|---|
| Pressure vessels (S-080) | 1.5 | 2.0 (typical, verified by test) |
| Lines and fittings, hazardous fluid | 1.5 | 4.0 |
| Lines and fittings, non-hazardous | 1.5 | 2.5 to 4.0 |
| Ground support equipment | per B31.3 | per B31.3 |

The practical result on a small-bore tubing run is that the required wall for pressure is almost always far below the smallest wall you can actually buy and handle. A 0.25 in OD 316L tube at 3.5 MPa needs 0.1 mm of wall by B31.3 and ships with 0.7 mm, a 560 percent margin. **On small tubing the wall is set by handling, bend radius and weldability, not by pressure.** Do not be surprised by a large margin; be surprised if there is not one, because that means the tube is genuinely highly loaded and everything else about it needs checking.

---

## Routing

**Minimize developed length.** Every meter costs pressure, mass, propellant residual and chilldown mass. This is in constant tension with everything else on this list.

**Use tube bends, not fittings, wherever possible.** A bend costs `L/D = 12`; a pair of elbows and a nipple costs `L/D = 60` plus two leak paths plus two joints to inspect. The standard aerospace practice is to bend continuous tube runs and use fittings only where a joint is genuinely needed for assembly or maintenance.

**Bend radius.** Minimum `r/D = 3` for hydraulically clean bends, and the tube bender's minimum for the wall thickness. Tighter bends wrinkle the inside wall and thin the outside wall. Wall thinning at a bend is approximately

```
t_outside / t_nominal ~ (2*R/D - 1) / (2*R/D)
```

At `R/D = 3` that is a 17 percent thinning on the outer wall, which must be accounted for in the pressure design.

**Provide flexibility deliberately.** A straight rigid run between two hard points is a thermal stress problem waiting to happen. Route with an offset, an expansion loop, or a deliberate bend so the line can absorb differential growth by bending rather than by loading the end fittings.

**Slope for drainage.** Ground systems handling liquids should be routed so they drain completely. Continuous slope, no local low points, drain ports at the low points that exist. A trapped pocket of propellant is a hazard at teardown and a source of contamination on the next run.

**Avoid dead legs.** A branch that is capped or normally isolated traps fluid. In a cryogenic system it becomes a geysering source; in a hazardous fluid system it becomes a passivation problem; in an oxygen system it becomes an adiabatic compression site. If a dead leg is unavoidable, keep it as short as possible (a good rule is length less than 3 diameters) and provide a vent or drain.

**Separate incompatible fluids.** Fuel and oxidizer lines should not share a bundle, a support, or a common cavity where a leak from one could reach the other. Physical separation, a barrier, or a vented interspace. For hypergolic systems this is a hard requirement, not a preference.

**Instrumentation ports.** Put them where the reading means something: pressure taps in straight runs with adequate approach length, temperature probes in the flow rather than in a stagnant well unless you specifically want the wall temperature. Every port is a leak path and a stress concentration, so do not add them casually, but do not omit the ones you will need to troubleshoot with, because retrofitting a port is far more expensive than installing one.

**Access.** Every joint must be reachable with the tool that torques it, and every joint that will be leak checked must be reachable with the sniffer or the bag. Route the plumbing before finalizing the structure if you possibly can.

---

## Supports and dynamics

**Support spacing** is set by three criteria, and the governing one varies:

1. **Deflection.** Limit midspan sag to something small, typically 2 to 3 mm, so the line stays where the model says it is.
2. **Stress.** Bending stress from self-weight plus fluid weight plus any dynamic load.
3. **Natural frequency.** Keep the first bending mode clear of the excitation environment. This is usually the governing criterion on a launch vehicle.

The first bending frequency of a simply supported span is

```
f1 = (pi / 2) * sqrt( E*I / (m' * L^4) )
```

with `m'` the mass per unit length including the fluid. Note the `L^-2` dependence: halving the span quadruples the frequency. If a line is rattling, the fix is almost always another clamp, not a stiffer tube.

**Target a first mode above the random vibration input roll-off**, typically above 100 to 200 Hz for launch vehicle plumbing. Lines that resonate in the launch environment fail at the fittings, because that is where the stress concentrates.

**Clamp design.** A clamp that grips too hard fretting-wears the tube; one that grips too loosely lets it move and fret anyway. Use cushioned clamps (Adel-style with elastomer or PTFE cushion) sized for the tube OD, and do not clamp directly against a weld or a fitting.

---

## Thermal growth and contraction

Cryogenic systems shrink, and the amount is larger than intuition suggests:

| Material | Integrated contraction, 293 K to 77 K | 293 K to 20 K |
|---|---|---|
| 304/316 stainless | 0.30 % | 0.31 % |
| Aluminum 6061 | 0.41 % | 0.42 % |
| Copper | 0.32 % | 0.33 % |
| Titanium 6Al-4V | 0.17 % | 0.17 % |
| Invar 36 | 0.04 % | 0.04 % |
| PTFE | 1.9 % | 2.1 % |
| Most elastomers | 1 to 2 % | (glassy, see below) |

A 3 m stainless LN2 line shrinks 9 mm. If both ends are rigidly anchored, that displacement has to go somewhere: either into the line as compressive stress and buckling, or into the anchors as load. A 3 m aluminum line to LH2 shrinks 13 mm.

**Accommodation options,** in rough order of preference:

1. **Routing flexibility.** An offset or an expansion loop absorbs growth by bending. Free, reliable, and the first choice.
2. **Bellows expansion joint.** Effective and compact, but a bellows is a pressure boundary with a fatigue life, and it must be restrained against pressure thrust or it will extend catastrophically.
3. **Flex hose.** Absorbs motion in any direction but adds significant pressure drop and has its own life limits.
4. **Sliding supports.** Let the line move axially through a guide, restrain it laterally.

Note the PTFE number. A PTFE-lined component or a PTFE seal contracts six times as much as the stainless around it, which is why PTFE static seals lose compression at cryogenic temperature and why spring-energized seals exist.

---

## Design rules of thumb

| Rule | Value | Why |
|---|---|---|
| Pressure drop sensitivity | `dP ~ D^-5` | Use actual ID, not nominal size |
| Developed length vs straight-line | 1.3 to 2.0 x | Routing is never straight |
| Feed line dP budget | 5 to 15 % of tank pressure | Larger fractions drive tank mass hard |
| Minimum bend radius | `r/D >= 3` | Below this, wall thinning and wrinkling |
| Outer wall thinning at a bend | `~ (2R/D - 1)/(2R/D)` | 17 % at `R/D = 3` |
| Dead leg length | `< 3 D` | Longer traps fluid and creates hazards |
| Support spacing for frequency | `f1 ~ 1/L^2` | Halving span quadruples frequency |
| Target first bending mode | `> 100 to 200 Hz` | Above the launch random vibration content |
| Small tube wall | Set by handling, not pressure | B31.3 margin is typically 300 to 600 % |
| Minor loss share of total dP | 20 to 50 % in a typical vehicle run | Do not neglect fittings |
| Flex hose penalty | ~0.6 added K per meter | Plus a much higher friction term |

---

## Failure modes

**Undersized line found late.** The classic program failure. The pressure budget does not close, tank pressure has to rise, tank wall grows, mass grows, and the fix at that point is expensive. Prevent it by carrying honest minor losses and by sizing with margin, not to the exact budget.

**Vibration fatigue at fittings.** Lines fail where they are stiffest, which is at the fitting. A line with inadequate support cracks at the flare or at the weld, not in the middle of the span.

**Thermal ratcheting.** A cryogenic line that is rigidly constrained yields slightly on each cooldown and slightly on each warmup, accumulating deformation cycle by cycle. Eventually it buckles or the anchor fails.

**Erosion at bends.** High velocity plus entrained particulate plus a change of direction. The outside of the bend thins. Common in slurry service and in systems with poor cleanliness control.

**Water hammer from valve closure.** Covered in [WaterHammer.md](WaterHammer.md). The line is the component that fails, but the valve is the cause.

**Flow-induced vibration.** A line with a high velocity gas flow past a branch tee can generate acoustic tones at the branch (a Helmholtz or quarter-wave resonance) with enough energy to fatigue small-bore instrumentation lines. Small-bore branches off high-velocity gas lines are the classic failure location.

**Chilldown two-phase surge.** Covered in [CryogenicSystems.md](CryogenicSystems.md). A line being chilled contains alternating slugs of liquid and vapor, and each slug arrival is a small water hammer event.

**Galvanic corrosion at dissimilar metal joints.** An aluminum line into a stainless fitting with an electrolyte present (which on a launch site means salt fog) corrodes the aluminum. Isolate, coat, or use compatible alloys.

---

## Operations

**Cleaning and cleanliness verification.** Lines are cleaned before installation, not after, because you cannot clean an installed system properly. Solvent flush, dry, cap both ends immediately. For oxygen service the requirement is much more stringent; see [CleanlinessAndContamination.md](CleanlinessAndContamination.md).

**Proof and leak test.** Proof pressure (typically 1.5 x MEOP) demonstrates strength; leak test at MEOP demonstrates the joints. Proof with a liquid where possible, because a pneumatic proof test stores enough energy to be genuinely dangerous. If a pneumatic proof is unavoidable, barricade and clear the area.

**Purge and inerting.** Any line that has contained a hazardous fluid must be purged before it is opened. See [OperationsAndPurge.md](OperationsAndPurge.md).

**Post-modification flow verification.** After any plumbing change, re-verify the flow rate. It is extremely easy to install one wrong fitting, one wrong tube size, or one valve backwards, and the system model will not tell you.

---

## Worked example

A hydrazine feed line, 2.5 m developed length, 0.045 kg/s at 293.15 K, inlet at 2.40 MPa. Routing has four r/D = 3 bends and one tee (flow through the run), plus two AN flare unions. Pressure drop budget 50 kPa. Design pressure 3.5 MPa. Hydrazine service velocity limit 6 m/s.

**Velocity constraint:**

```
D = sqrt( 4 * 0.045 / (pi * 1008.5 * 6.0) ) = 3.08 mm
```

**Pressure drop constraint:** iterating gives `D = 4.905 mm`. The pressure drop budget governs, by a wide margin, which is typical for a long run.

**Standard tube selection.** The smallest stocked size with `ID >= 4.905 mm` is 0.25 in OD x 0.028 in wall, giving `ID = 4.928 mm`.

**Result at the selected size:**

| Quantity | Value |
|---|---|
| Equivalent length from fittings | 0.335 m |
| Total effective length | 2.835 m |
| Relative roughness | 3.04e-4 |
| Reynolds number | 1.19e4 |
| Darcy friction factor | 0.0301 |
| Velocity | 2.34 m/s |
| Friction pressure drop | 47.8 kPa |
| Minor loss pressure drop | 1.1 kPa |
| **Total pressure drop** | **48.9 kPa** |
| Outlet pressure | 2.351 MPa |
| B31.3 required wall | 0.108 mm |
| Actual wall | 0.711 mm |
| Wall margin | +561 % |
| Hoop stress at MEOP | 12.1 MPa |
| Dry mass | 0.252 kg |

Two observations. The velocity of 2.34 m/s is well under the 6 m/s limit, so this line is entirely pressure-drop sized. And the wall margin is enormous, which is the expected result for small-bore tubing: the wall is set by what you can buy and bend, not by pressure.

Reproduce with:

```python
from Line import Line

feedLine = Line()
feedLine.setInputs({'fluid': 'N2H4', 'massFlow': 0.045, 'length': 2.5,
                    'inletPressure': 2.4e6, 'inletTemperature': 293.15,
                    'fittings': {'bend 90 r/d=3': 4, 'tee run': 1},
                    'lossCoefficients': {'an flare union': 2},
                    'allowablePressureDrop': 5.0e4,
                    'designPressure': 3.5e6, 'service': 'hydrazine'})
feedLine.sizeDiameter()
feedLine.selectStandardTube()
feedLine.calculateWallThickness()
feedLine.calculateMass()
print(feedLine.generateReport())
```

---

## Standards

| Standard | Scope |
|---|---|
| ASME B31.3 | Process piping: design, materials, fabrication, examination, testing |
| ASME B31.12 | Hydrogen piping and pipelines |
| ASME BPVC Section VIII Div. 1 | Pressure vessels |
| AIAA S-080 | Space systems: metallic pressure vessels, pressurized structures and pressure components |
| AIAA S-081 | Space systems: composite overwrapped pressure vessels |
| NASA-STD-8719.17 | NASA requirements for ground-based pressure vessels and pressurized systems |
| MSFC-SPEC-3679 | Welding, fusion, aerospace fluid systems hardware |
| SAE AS1290 | Graphical symbols for aircraft hydraulic and pneumatic systems |
| ASTM A269 / A213 | Seamless austenitic stainless tubing |
| NASA-STD-6001 | Flammability, offgassing and compatibility requirements, includes oxygen velocity guidance |
| ASTM G88 | Designing systems for oxygen service |
| CGA G-4.4 | Oxygen pipeline and piping systems |

---

## Tool interface

The [`Line`](../Line.py) class implements the sizing, pressure drop and wall thickness calculations.

```python
from Line import Line

# Size from a pressure drop budget and a velocity limit
line = Line()
line.setInputs({'fluid': 'N2H4', 'massFlow': 0.045, 'length': 2.5,
                'inletPressure': 2.4e6, 'inletTemperature': 293.15,
                'fittings': {'bend 90 r/d=3': 4},
                'allowablePressureDrop': 5.0e4,
                'designPressure': 3.5e6, 'service': 'hydrazine'})
line.sizeDiameter()          # binding constraint of velocity and dP
line.selectStandardTube()    # snap up to a stocked size, re-solve
line.calculateWallThickness()
line.calculateMass()

# Analyze a known geometry
gasLine = Line()
gasLine.setInputs({'fluid': 'Helium', 'massFlow': 0.005, 'length': 10.0,
                   'inletPressure': 20e6, 'inletTemperature': 293.15,
                   'innerDiameter': 0.006, 'surface': 'drawn tube'})
gasLine.calculatePressureDrop()
print(gasLine.machNumber)     # exit Mach; raises ChokedFlowError at 1.0
```

Supporting lookups in [`utils`](../utils.py): `frictionFactor`, `roughnessTable`, `materialProperties`, `b31_3WallThickness`. Fitting and loss tables are `Line.EQUIVALENT_LENGTH_RATIOS`, `Line.LOSS_COEFFICIENTS`, `Line.VELOCITY_LIMITS`, `Line.STANDARD_TUBE_SIZES_IN`.

---

## References

1. Crane Co., *Flow of Fluids Through Valves, Fittings, and Pipe*, Technical Paper No. 410.
2. Churchill, S. W., "Friction Factor Equation Spans All Fluid-Flow Regimes", *Chemical Engineering*, Vol. 84, No. 24, 1977.
3. Haaland, S. E., "Simple and Explicit Formulas for the Friction Factor in Turbulent Pipe Flow", *Journal of Fluids Engineering*, Vol. 105, 1983.
4. Darby, R., *Chemical Engineering Fluid Mechanics*, 2nd ed., Marcel Dekker, 2001 (3-K method).
5. Idelchik, I. E., *Handbook of Hydraulic Resistance*, 4th ed., Begell House, 2007.
6. ASME B31.3, *Process Piping*.
7. AIAA S-080A-2018, *Space Systems -- Metallic Pressure Vessels, Pressurized Structures, and Pressure Components*.
8. Barron, R. F., *Cryogenic Systems*, 2nd ed., Oxford University Press, 1985.
9. NASA-STD-6001B, *Flammability, Offgassing, and Compatibility Requirements and Test Procedures*.
10. Huzel, D. K. and Huang, D. H., *Modern Engineering for Design of Liquid-Propellant Rocket Engines*, AIAA, 1992.
