[Home](../../README.md) > Valves

# Valves

## Contents

- [Overview](#overview)
- [Valve types and selection](#valve-types-and-selection)
- [Governing physics](#governing-physics)
  - [Flow coefficient](#flow-coefficient)
  - [Liquid sizing and choked liquid flow](#liquid-sizing-and-choked-liquid-flow)
  - [Gas sizing and choked gas flow](#gas-sizing-and-choked-gas-flow)
  - [Cavitation and flashing in valves](#cavitation-and-flashing-in-valves)
  - [Converting Cv to K and to an equivalent orifice](#converting-cv-to-k-and-to-an-equivalent-orifice)
- [Characteristics and valve authority](#characteristics-and-valve-authority)
- [Actuation](#actuation)
- [Seats, seals and leakage classes](#seats-seals-and-leakage-classes)
- [Response time and sequencing](#response-time-and-sequencing)
- [Design procedure](#design-procedure)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Operations](#operations)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A valve is an orifice whose area you can change. Everything else about it -- the actuator, the stem seal, the body, the trim -- exists to make that area change reliably, at the right speed, without leaking.

Almost every valve question reduces to one of four:

1. **What flow coefficient do I need?** Sizing, liquid or gas, choked or unchoked.
2. **What happens when it chokes?** The pressure recovery factor `FL` and the terminal pressure drop ratio `xT` determine when, and the answers are wildly different between valve types.
3. **How does it behave part open?** The inherent characteristic, the installed characteristic, and valve authority.
4. **What does it take to move it?** Seat load, pressure unbalance, actuator sizing, response time.

The question that gets asked least and matters most is the third. A valve sized correctly at full open can be completely uncontrollable in the system it is installed in, because when the line resistance dominates, the installed characteristic bears no resemblance to the inherent one and all of the control happens in the first ten percent of travel.

---

## Valve types and selection

| Type | Function | FL | xT | Cv per in^2 | Notes |
|---|---|---|---|---|---|
| Globe | Throttling, control | 0.90 | 0.72 | 12 | The control valve standard. High recovery factor, resists cavitation. Enormous pressure drop when open (`L/D = 340`) |
| Globe, cage-guided | Throttling, high dP | 0.90 | 0.75 | 10 | Multi-stage or characterized cage trim for anti-cavitation |
| Angle | Throttling, erosive service | 0.90 | 0.72 | 14 | Self-draining, tolerant of flashing |
| Ball, full bore | Isolation, fast on/off | 0.60 | 0.15 | 45 | Near-zero dP open (`L/D = 3`). Quarter turn. Poor throttling. **Chokes early on gas** |
| Ball, reduced bore | Isolation | 0.68 | 0.22 | 28 | Lighter, cheaper, slightly better recovery |
| Ball, segmented (V-port) | Throttling | 0.66 | 0.30 | 25 | Characterized ball for control duty |
| Butterfly | Isolation, large line | 0.55 | 0.15 | 35 | Lightest and cheapest per unit area. Poor recovery, chokes very early |
| Butterfly, high performance | Isolation and coarse control | 0.70 | 0.30 | 30 | Offset disc, better seat life and recovery |
| Gate | Isolation only | 0.80 | 0.30 | 40 | Never throttle a gate valve; the disc chatters and erodes |
| Needle | Fine metering, small flows | 0.95 | 0.80 | 1.5 | Highest recovery factor of any type. Very low capacity |
| Poppet / solenoid | Fast on/off, small line | 0.90 | 0.72 | 8 | Fast, but the pressure unbalance force limits the size that a solenoid can drive |
| Plug | Isolation and coarse control | 0.84 | 0.55 | 30 | Compact quarter turn, good for slurries |

**How to read the FL and xT columns.** `FL` is the liquid pressure recovery factor. A high `FL` means the valve recovers little pressure downstream of the vena contracta, so the vena contracta pressure stays close to the outlet pressure and the valve resists cavitation. A low `FL` means strong recovery, a much lower vena contracta pressure, and cavitation at differentials a globe valve would sail through.

`xT` is the terminal pressure drop ratio: the value of `dP/P1` at which the gas flow chokes. A globe valve chokes at `x = 0.72`; a butterfly valve chokes at `x = 0.15`. That is not a subtlety. A butterfly valve in a gas line chokes at a pressure ratio the globe valve does not even notice, which means its capacity is capped far below what a naive `Cv` calculation would suggest.

**Selection guidance:**

| Requirement | Choose |
|---|---|
| Isolation, minimum pressure drop | Ball, full bore |
| Isolation, large diameter, mass critical | Butterfly |
| Throttling with a control loop | Globe, equal percentage trim |
| High differential liquid, cavitation risk | Globe with anti-cavitation (multi-stage) trim |
| Fast actuation, small line | Solenoid poppet |
| Fine flow metering, manual | Needle |
| Cryogenic isolation | Ball or gate with extended bonnet and metal or PCTFE seat |
| Hazardous fluid, zero external leakage | Bellows-sealed stem, or a fully welded body |
| Oxygen service | Metal or PCTFE seat, no hydrocarbon lubricant, slow opening |

---

## Governing physics

### Flow coefficient

`Cv` is defined as the number of US gallons per minute of 60 degF water that pass through the valve with a 1 psi differential. It is an imperial definition wearing an engineering hat and it will not go away, so the right move is to convert it once, at the boundary, and work in SI internally:

```
mdot [kg/s] = Cv * 2.40172e-5 * sqrt( rho [kg/m^3] * dP [Pa] )
```

The constant is derived, not looked up: `1 gpm = 6.30902e-5 m^3/s`, `1 psi = 6894.757 Pa`, water at 60 degF is 999.0 kg/m^3.

`Kv`, the metric equivalent, is m^3/h of water at 1 bar:

```
Kv = 0.8646 * Cv
```

Note that `Cv` is not dimensionless and is not a property of the fluid. It is a property of the valve at a given travel, and the same valve has a different `Cv` at every position.

### Liquid sizing and choked liquid flow

IEC 60534-2-1, in the SI form used by [`Valve`](../Valve.py):

```
mdot = Cv * N * sqrt( rho * dP_sizing )          N = 2.40172e-5
```

The subtlety is entirely in `dP_sizing`, which is **not** simply `P1 - P2`. It is capped at the choked value:

```
FF        = 0.96 - 0.28 * sqrt( Pv / Pc )         liquid critical pressure ratio factor
dP_choked = FL^2 * ( P1 - FF * Pv )
dP_sizing = min( P1 - P2, dP_choked )
```

`FF` accounts for the fact that a fluid near its critical point flashes at a pressure well above its vapor pressure. For a fluid far from critical (`Pv/Pc` small) `FF` approaches 0.96.

**Sizing a choked valve on the full differential undersizes it.** If the actual differential is twice the choked differential, using the full value overpredicts flow by `sqrt(2) = 41` percent, so the valve you select will be 41 percent too small. This is one of the most common valve sizing errors and it is entirely avoidable.

### Gas sizing and choked gas flow

The gas equation is the liquid equation multiplied by an expansion factor `Y`:

```
x        = dP / P1                                pressure drop ratio
F_gamma  = gamma / 1.4                            specific heat ratio factor
x_choked = F_gamma * xT
x_used   = min( x, x_choked )
Y        = 1 - x_used / (3 * F_gamma * xT),  floored at 2/3

mdot = Cv * N * Y * sqrt( rho1 * x_used * P1 )
```

`rho1` is the inlet density. Note that `Y` falls linearly from 1.0 at zero differential to exactly 2/3 at the choking point, and is pinned at 2/3 beyond it. Once choked, further pressure drop buys nothing at all.

**Where the choking point actually is.** For nitrogen (`gamma = 1.4`, so `F_gamma = 1.0`) through a globe valve (`xT = 0.72`), choking is at `dP/P1 = 0.72`, i.e. `P2/P1 = 0.28`. Through a butterfly valve (`xT = 0.15`), choking is at `P2/P1 = 0.85`. A butterfly valve with only a 15 percent pressure drop is already at its capacity limit.

### Cavitation and flashing in valves

The service severity index is

```
sigma = (P1 - Pv) / (P1 - P2)
```

with the transitions set by the valve's own recovery factor:

| Condition | Threshold | Meaning |
|---|---|---|
| Choked cavitation | `sigma <= 1/FL^2` | Fully developed cavitation, flow no longer follows the dP relation |
| Incipient cavitation | `sigma <= 1.7/FL^2` | Audible, intermittent, erosion begins |
| Flashing | `P2 <= Pv` | Two-phase downstream, permanent |

For a globe valve (`FL = 0.90`) the choking threshold is `sigma = 1.23`. For a butterfly valve (`FL = 0.55`) it is `sigma = 3.31`. **The butterfly valve cavitates at nearly three times the `sigma`**, which in practice means it cavitates at differentials the globe valve handles cleanly. That is the single most useful consequence of the recovery factor.

**Cavitation and flashing are fixed differently.** Cavitation collapses bubbles against metal, and each collapse is a microjet impact. It is cured by:

- Staging the pressure drop across multiple restrictions in series (multi-stage trim, or two valves in series with an intermediate pressure)
- Moving to a higher `FL` trim
- Raising the downstream pressure with a fixed restriction downstream of the valve
- Moving the collapse zone off the wall (characterized cage trim directs the jets into the flow stream rather than into the body)

Flashing does not collapse and cannot be cured by trim, because the downstream pressure never recovers above vapor pressure. It is cured by raising the downstream pressure, or by accepting the erosion and specifying hardened trim and an angle-body valve that lets the two-phase jet exit cleanly rather than impinging.

### Converting Cv to K and to an equivalent orifice

To drop a valve into a line minor-loss budget you need `K`, referenced to a defined area. Equating the `Cv` and `K` pressure drop forms:

```
K = 2 * A_ref^2 / ( N^2 * Cv^2 )
```

with `A_ref` the nominal port area. To compare a valve against a fixed restriction:

```
A_equivalent = Cv * N / ( Cd * sqrt(2) )
```

These conversions are what let a valve and an orifice appear in the same pressure budget without switching unit systems mid-calculation.

---

## Characteristics and valve authority

### Inherent characteristic

The relationship between fractional travel `h` and fractional `Cv`, measured at **constant differential pressure**. It is a property of the trim alone.

| Characteristic | `f(h)` | Where used |
|---|---|---|
| Linear | `h` | Systems where the valve takes most of the pressure drop (high authority) |
| Equal percentage | `R^(h-1)`, `R = 50` | The default control trim. Equal percentage change in flow per equal change in travel |
| Quick opening | `sqrt(h)` | On/off service; most of the capacity in the first part of the stroke. Butterfly and gate valves are inherently quick-opening |

### Installed characteristic and valve authority

The installed characteristic is what you actually get once the valve is plumbed into a system whose resistance rises with flow. As the valve opens, more of the total pressure drop shifts to the line, the valve differential collapses, and the flow rises much less than the inherent curve promised.

The governing parameter is **valve authority**:

```
N_authority = dP_valve(full open) / dP_total(full open)
```

Modeling the rest of the system as a fixed resistance in series gives

```
q(h) = 1 / sqrt( (1 - N) + N / f(h)^2 )
```

| Authority | Consequence |
|---|---|
| `N > 0.5` | Installed curve close to inherent. Any characteristic works |
| `N = 0.2 to 0.5` | Equal percentage installs approximately linear. This is the design intent of equal percentage trim |
| `N < 0.2` | Every characteristic degenerates toward quick-opening. The valve does all its work in the first few percent of travel and is effectively on/off |

**This is the reason equal percentage trim exists.** Its rising slope partially cancels the falling valve differential, so the installed curve comes out closer to linear than the inherent curve is. Selecting linear trim for a low-authority installation produces a valve that is unusable for control and nobody can explain why.

Worked numerically, at `N = 0.2` with equal percentage trim:

| Travel | Inherent Cv fraction | Installed flow fraction |
|---|---|---|
| 0.0 | 0.000 | 0.000 |
| 0.2 | 0.044 | 0.097 |
| 0.4 | 0.096 | 0.210 |
| 0.6 | 0.209 | 0.431 |
| 0.8 | 0.457 | 0.755 |
| 1.0 | 1.000 | 1.000 |

The installed curve is close to linear, which is exactly what a control loop wants. Repeat the same calculation with linear trim at the same authority and the result is strongly quick-opening.

**Rangeability.** The ratio of maximum to minimum controllable `Cv`, typically 50:1 for a globe valve with equal percentage trim, and much lower for a butterfly. Below the minimum controllable `Cv` the valve is on the seat and the flow is not a repeatable function of the command.

---

## Actuation

Three load contributions, all of which the actuator must overcome simultaneously at the worst condition:

**1. Seat load.** The contact force required to make the seat seal:

```
F_seat = sigma_sealing * pi * d_seat * w_contact
```

| Seat material | Sealing stress [MPa] | Notes |
|---|---|---|
| Elastomer (o-ring or lip) | 7 | Lowest load, narrowest temperature range |
| PTFE | 14 | Cold flows and creeps; loses load over time and at cryogenic temperature |
| PCTFE (Kel-F) | 28 | **The LOX-compatible soft seat of choice**. Better cryogenic dimensional stability than PTFE |
| PEEK | 35 | High temperature, good creep resistance |
| Vespel (polyimide) | 45 | High temperature, hygroscopic (absorbs moisture and swells) |
| Metal-to-metal, lapped | 200 | The only option for hot gas or long-term storage. Very high actuation load |

**2. Pressure unbalance.** The differential acting over the unbalanced seat area:

```
F_unbalance = dP * pi * d_seat^2 / 4
```

For a poppet or globe valve at high pressure this dominates everything. A 12 mm seat at 20 MPa is 2260 N of unbalance, which is a large actuator. **Balanced trim** exists specifically to cancel this by porting the downstream pressure to the back of the plug, at the cost of a balance seal that is itself a leak path.

**3. Spring preload.** For a fail-safe valve, the return spring must close the valve against the full differential with no actuation power. That preload is a load the actuator fights on every opening stroke.

```
F_actuator = ( F_seat + F_unbalance + F_spring ) / eta_mechanism
```

with `eta_mechanism` typically 0.7 to 0.9.

**Quarter-turn torque.** For ball and butterfly valves, a first-cut breakaway torque estimate:

```
T = C_torque * dP * d^3
```

with `C_torque` around 0.04 to 0.06 for ball and butterfly valves. **This is a rough estimate only.** Real breakaway torque depends on seat material, seat interference, temperature history, and how long the valve has been sitting closed. Size actuators from vendor torque data with a safety factor of at least 1.5, and remember that breakaway after a long cold soak or a long storage period can be several times the catalog running torque. Cryogenic ball valves in particular can require two to three times their ambient breakaway torque after a cold soak, because the seat has shrunk onto the ball.

**Actuator types:**

| Type | Speed | Force density | Notes |
|---|---|---|---|
| Solenoid | 5 to 50 ms | Low | Direct-acting is limited to small orifices; pilot-operated overcomes that but needs a pressure differential to work |
| Pneumatic piston | 50 to 500 ms | High | The workhorse for propulsion. Needs a pneumatic supply and its own control valves |
| Pneumatic diaphragm | 200 ms to 2 s | Medium | Standard for process control valves, good modulation |
| Electric (motor) | 1 to 30 s | High | Slow but positionable and needs no pneumatic supply |
| Pyrotechnic | 1 to 10 ms | Very high | One shot. Used for normally-closed isolation on spacecraft |
| Manual | operator dependent | High | Never rely on manual valve position in a hazardous sequence without position indication |

---

## Seats, seals and leakage classes

**Internal (seat) leakage** is classified by ANSI/FCI 70-2:

| Class | Allowable seat leakage |
|---|---|
| I | Not tested (by agreement) |
| II | 0.5 % of rated capacity |
| III | 0.1 % of rated capacity |
| IV | 0.01 % of rated capacity (typical metal seat) |
| V | 5e-4 mL/min per mm of seat diameter per bar dP (water) |
| VI | Bubble-tight, defined bubble count per minute by seat size (soft seat) |

For propulsion work, Class VI or better is the usual requirement on a propellant isolation valve, and it is often expressed instead as an absolute helium leak rate (for example, `< 1e-5 scc/s He`) because that is what can actually be measured on flight hardware. See [Leaks.md](Leaks.md).

**External leakage** is a separate requirement and is usually the harder one. Stem seals are the weak point:

- **Packing.** Adjustable, serviceable, and always leaks a little. Unacceptable for hazardous fluids.
- **O-ring stem seal.** Better, but a dynamic o-ring wears and the seal degrades with cycles.
- **Bellows stem seal.** Zero external leakage by construction: the bellows is a welded pressure boundary with no sliding interface. The bellows has a defined cycle life and a pressure thrust that must be reacted. **This is the correct choice for hydrazine, hypergolics and any toxic fluid.**
- **Fully welded body with a magnetic or pyrotechnic actuator.** Zero leak paths, zero serviceability.

**Material compatibility for seats** is covered in [MaterialsCompatibility.md](MaterialsCompatibility.md). Two hard rules to carry here:

- **No hydrocarbon lubricants anywhere in an oxygen system.** Use Krytox or a similar perfluorinated grease, and only where it is genuinely required.
- **No Buna-N (nitrile) in hydrazine.** It degrades and catalyzes decomposition. Use EPDM, Teflon or metal.

---

## Response time and sequencing

**Opening and closing time** matters for two independent reasons: sequencing and water hammer.

The stroke time of a pneumatically actuated valve is set by how fast the actuator volume can be filled or vented through the pilot valve and the pilot line:

```
t_stroke ~ V_actuator / ( Cv_pilot * f(P_supply, P_actuator) )
```

which means the pilot line and pilot valve, not the main valve, usually set the response time. A common and expensive mistake is to specify a fast main valve and then feed it through a long, small-bore pilot line.

**Water hammer.** The critical closure time is the pipe period:

```
t_critical = 2 * L / a
```

with `a` the pressure wave speed. Closing faster than `t_critical` produces the full Joukowsky surge `dP = rho * a * dV`; closing slower reduces it approximately in proportion to `t_critical / t_close`. See [WaterHammer.md](WaterHammer.md).

The design tension is real: fast closure is wanted for a safety shutoff and for a crisp thrust cutoff, and slow closure is wanted to avoid surge. Resolve it by computing the surge explicitly rather than by choosing a closure time by feel.

**Effective closure time is not stroke time.** A valve with an equal-percentage or quick-opening characteristic does most of its flow reduction in the last part of its travel. The effective closure time for surge purposes is the time over which the flow actually changes, which can be a small fraction of the total stroke time. This is the reason a "slow" valve can still produce a full Joukowsky surge.

---

## Design procedure

**1. Establish the duty.** Fluid, `P1`, `P2`, `T1`, required `mdot`, and whether the valve is isolation, throttling or control.

**2. Select the type** from the selection table, considering pressure drop when open, actuation, seat compatibility and leakage class.

**3. Check the choking condition** before sizing. For liquid, compute `dP_choked`. For gas, compute `x_choked = F_gamma * xT` and compare against `x`.

**4. Size the `Cv`** using the capped sizing differential.

**5. Check cavitation** for liquid service. If `sigma` is below `1.7/FL^2`, either change trim, stage the drop, or accept damage.

**6. Set the design travel.** Do not size a control valve to be full open at the design flow: aim for 60 to 80 percent travel, so there is capacity margin above and controllability below.

**7. Compute valve authority** and confirm the characteristic is right for it.

**8. Size the actuator** at the worst-case differential, which for a fail-closed valve is often the full upstream pressure against a closed downstream, not the operating differential.

**9. Set the closure time** from the water hammer calculation and confirm the actuator can achieve it.

**10. Specify the leakage class**, both internal and external, in units that can be measured.

---

## Design rules of thumb

| Rule | Value | Why |
|---|---|---|
| Control valve design travel | 60 to 80 % open at design flow | Capacity margin above, controllability below |
| Minimum controllable travel | > 10 % | Below this the trim is on the seat and flow is not repeatable |
| Valve authority target | `> 0.25` | Below this the installed characteristic collapses |
| Trim choice at low authority | Equal percentage | Cancels the falling valve differential |
| Never throttle | Gate, ball (unless V-ported) | Disc/seat chatter and erosion |
| Globe valve open pressure drop | `L/D = 340` | Never use as an isolation valve |
| Cavitation margin | `sigma > 2 / FL^2` | Keeps clear of incipient with temperature margin |
| Actuator sizing factor on vendor torque | `>= 1.5` | Breakaway after cold soak or long storage far exceeds running torque |
| Cryogenic breakaway multiplier | 2 to 3 x ambient | Seat shrinks onto the ball |
| Pilot line sizing | Sized for stroke time, not for leakage | The pilot circuit sets the response |
| Hazardous fluid stem seal | Bellows | The only zero-external-leakage sliding-free option |

---

## Failure modes

**Undersized because the choking limit was ignored.** Sizing on the full differential when the valve is choked yields a valve up to 40 percent too small. The system does not reach flow and nobody can find the error because the arithmetic is right.

**Cavitation damage.** Trim erosion, body erosion downstream of the trim, noise. Fixed by staging or by trim selection, not by material alone.

**Seat leakage after a single particle.** A soft seat that has swallowed one hard particle leaks permanently. Filtration upstream of any valve that has to seal is not optional.

**Galling of the stem or the ball.** Austenitic stainless against austenitic stainless galls, and a galled stem seizes. Plate, use dissimilar hardness, or use a different alloy pair.

**Cold-soak seize.** A ball valve that closed at ambient and then cold-soaked can require several times the ambient breakaway torque. Actuators sized on catalog running torque fail to open.

**Stem seal leakage.** Dynamic o-rings wear. On a hazardous fluid this is a personnel hazard, not a maintenance item.

**Actuator supply failure.** A pneumatically actuated valve does what its spring tells it to when the supply is lost. That is a deliberate design choice (fail open, fail closed, fail as-is) and it must be made explicitly for every valve, then verified by test.

**Position indication disagreeing with actual position.** A limit switch that indicates on actuator position, not stem position, will happily report "closed" for a valve whose stem has sheared. Where valve position matters for safety, indicate on the stem.

**Water hammer from fast closure.** See [WaterHammer.md](WaterHammer.md). The valve survives; the line and the instrumentation do not.

**Chatter in a check valve or a relief valve.** Covered in [FlowControlDevices.md](FlowControlDevices.md).

---

## Operations

**Seat leakage test.** Pressurize upstream with the downstream vented and measure the leak. For a Class VI requirement this is a bubble count; for flight hardware it is a helium leak rate.

**Stroke test.** Verify full travel, verify timing in both directions, verify position indication at both ends. Do it at the actual supply pressure, not at shop air pressure.

**Functional test at differential.** A valve that strokes freely with no pressure may not stroke at all against its design differential. Test at pressure.

**Cycle life.** Soft seats and stem seals wear. Track cycle counts on flight hardware and on any valve in a hazardous system.

**Lubrication.** Any lubricant is a contaminant somewhere. In oxygen service the only acceptable lubricants are perfluorinated (Krytox and similar), and they must be applied sparingly and documented. In hydrazine service, nothing organic.

**Do not exercise a valve to "free it up" in a hazardous system without a plan.** A stuck valve that suddenly frees can produce exactly the fast transient the system was designed to avoid.

---

## Worked example

A hydrazine isolation valve, 0.045 kg/s at 293.15 K, 2.35 MPa inlet, 50 kPa allowable drop when open. Full-bore ball valve, 6.35 mm (0.25 in) port, PTFE seat. Total system pressure drop 250 kPa.

**Sizing:**

```
Cv = mdot / ( N * sqrt(rho * dP) )
   = 0.045 / ( 2.40172e-5 * sqrt(1008.5 * 50000) )
   = 0.2639
```

**Choking check:** `Pv = 1.43 kPa`, `Pc = 14.7 MPa`, so `FF = 0.96 - 0.28*sqrt(1.43e3/14.7e6) = 0.957`. With `FL = 0.60`:

```
dP_choked = 0.60^2 * (2.35e6 - 0.957 * 1.43e3) = 845.5 kPa
```

The actual 50 kPa differential is far below that, so the valve is unchoked and the simple sizing stands.

**Cavitation check:** `sigma = (2.35e6 - 1.43e3)/5.0e4 = 47.0`, against a choked threshold of `1/0.60^2 = 2.78`. No cavitation, with a very large margin.

**Valve authority:** `N = 50 kPa / 250 kPa = 0.20`. That is at the low end. For an isolation valve it does not matter, but if this valve were expected to throttle, equal percentage trim would be mandatory and even then the controllability would be marginal.

**Actuation:** PTFE seat at 14 MPa sealing stress, 6.35 mm seat, 2 percent contact width:

| Contribution | Value |
|---|---|
| Seat load | 35.5 N |
| Pressure unbalance at 50 kPa | 1.6 N |
| Actuation force (eta = 0.8) | 46.3 N |

Note that the unbalance is small **at the operating differential**. At the worst case, the valve closed against full 2.35 MPa upstream with the downstream vented, the unbalance is `2.35e6 * pi * 0.00635^2/4 = 74.4 N`, which is where the actuator must actually be sized.

Reproduce with:

```python
from Valve import Valve

isolationValve = Valve()
isolationValve.setInputs({'fluid': 'N2H4', 'upstreamPressure': 2.35e6,
                          'downstreamPressure': 2.30e6, 'upstreamTemperature': 293.15,
                          'massFlow': 0.045, 'valveType': 'ball full bore',
                          'nominalSize': 0.00635, 'seatMaterial': 'ptfe',
                          'systemPressureDrop': 2.5e5})
isolationValve.sizeFlowCoefficient()
isolationValve.calculateActuationLoad()
isolationValve.calculateCharacteristic()
print(isolationValve.generateReport())
```

---

## Standards

| Standard | Scope |
|---|---|
| IEC 60534-2-1 | Industrial control valves: flow capacity sizing equations for installed conditions |
| IEC 60534-8-3 | Control valve aerodynamic noise prediction |
| ISA-75.01.01 | Flow equations for sizing control valves (the ISA counterpart to IEC 60534-2-1) |
| ANSI/FCI 70-2 | Control valve seat leakage classification |
| API 598 | Valve inspection and testing |
| MSS SP-61 | Pressure testing of valves |
| NASA SP-8080 | Liquid rocket pressure regulators, relief valves, check valves, burst disks and explosive valves |
| MIL-V-25675 | Valve, hydraulic, general specification (aircraft) |
| SAE AS4941 | Valves, general specification for aerospace fluid systems |
| ASTM G88 | Designing systems for oxygen service, includes valve guidance |
| CGA V-9 | Compressed gas association standard for cylinder valves |

---

## Tool interface

The [`Valve`](../Valve.py) class implements sizing, choking, cavitation, characteristics and actuation.

```python
from Valve import Valve

valve = Valve()
valve.setInputs({'fluid': 'N2H4', 'upstreamPressure': 2.35e6,
                 'downstreamPressure': 2.30e6, 'upstreamTemperature': 293.15,
                 'massFlow': 0.045, 'valveType': 'ball full bore',
                 'nominalSize': 0.00635, 'systemPressureDrop': 2.5e5})

valve.sizeFlowCoefficient()        # required Cv, with the choking cap applied
valve.calculateActuationLoad()     # seat load, unbalance, actuator force, torque
curves = valve.calculateCharacteristic(21)   # inherent and installed curves plus authority
valve.convertToLossCoefficient()   # K and equivalent orifice area

# Forward problem: flow through a known Cv at partial travel
valve.flowCoefficient = 5.0
valve.travelFraction  = 0.4
valve.calculateMassFlow()
```

Lookup tables: `Valve.VALVE_TYPES` (FL, xT, capacity, torque factor, default characteristic), `Valve.SEAT_SEALING_STRESS`.

Key attributes after a solve: `requiredFlowCoefficient`, `flowCoefficientKv`, `isChoked`, `chokedPressureDrop`, `cavitationIndex`, `cavitationStatus`, `expansionFactor`, `lossCoefficient`, `equivalentOrificeArea`, `valveAuthority`, `actuationForce`, `actuationTorque`.

---

## References

1. IEC 60534-2-1:2011, *Industrial-process control valves -- Part 2-1: Flow capacity -- Sizing equations for fluid flow under installed conditions*.
2. ANSI/FCI 70-2, *Control Valve Seat Leakage*.
3. Emerson Process Management, *Control Valve Handbook*, 5th ed., 2019.
4. Baumann, H. D., *Control Valve Primer: A User's Guide*, 4th ed., ISA, 2009.
5. NASA SP-8080, *Liquid Rocket Pressure Regulators, Relief Valves, Check Valves, Burst Disks, and Explosive Valves*, 1973.
6. Crane Co., *Flow of Fluids Through Valves, Fittings, and Pipe*, Technical Paper No. 410.
7. ASTM G88-13, *Standard Guide for Designing Systems for Oxygen Service*.
8. Huzel, D. K. and Huang, D. H., *Modern Engineering for Design of Liquid-Propellant Rocket Engines*, AIAA, 1992.
