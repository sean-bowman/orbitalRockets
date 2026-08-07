[Home](../../README.md) > Flow Control Devices

# Flow Control Devices

Regulators, relief valves, burst discs, check valves, filters and cavitating venturis.

## Contents

- [Overview](#overview)
- [Regulators](#regulators)
- [Relief valves](#relief-valves)
- [Burst discs](#burst-discs)
- [The pressure set point ladder](#the-pressure-set-point-ladder)
- [Check valves](#check-valves)
- [Filters](#filters)
- [Cavitating venturis](#cavitating-venturis)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Operations](#operations)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

These six devices are grouped because they all control a flow or a pressure without a command. Once installed they do what their physics dictates, and their failure modes are consequently the ones a control system cannot compensate for.

| Device | Controls | Failure mode that matters |
|---|---|---|
| Regulator | Downstream pressure | Fails open, overpressurizing everything downstream |
| Relief valve | Maximum pressure | Fails to lift, or lifts during normal operation |
| Burst disc | Maximum pressure, last resort | Bursts early (nuisance) or late (no protection) |
| Check valve | Flow direction | Chatters and destroys itself, or leaks backwards |
| Filter | Particulate | Plugs, or is bypassed, or was never sized for life |
| Cavitating venturi | Mass flow, independent of downstream | Unchokes silently and stops regulating |

---

## Regulators

**A regulator does not hold a constant pressure.** It holds a pressure that varies with flow and with inlet pressure, and the resulting band is what the downstream system actually sees.

### The three effects

**Droop.** As flow increases, the sensing element moves further to open the poppet further. In a spring-loaded regulator that changes the spring force, and the outlet pressure falls. Droop is quoted as a fraction of set pressure at rated flow.

**Supply pressure effect (SPE).** The inlet pressure acts on the poppet, usually in the **opening** direction. As the supply falls over a blowdown, the poppet closes slightly and **the outlet pressure rises**. That sign is counterintuitive: a blowdown system's regulated pressure creeps UP as the bottle empties, which is the opposite of what most people expect.

**Lockup.** At zero flow the poppet must seat fully, and it takes a small overpressure to do it. The outlet pressure at zero flow is above the set pressure. That overshoot is what the downstream relief valve has to be set above.

### Regulator types

| Type | Droop | SPE | Lockup rise | Min differential | Notes |
|---|---|---|---|---|---|
| **Direct acting spring** | 15 % | -3 % | 5 % | 20 % | Simplest, most common, worst regulation |
| Two stage spring | 5 % | -0.5 % | 3 % | 25 % | Second stage sees a nearly constant inlet |
| **Dome loaded** | 3 % | -1 % | 2 % | 15 % | Best regulation; remotely adjustable. Needs a dome supply |
| Back pressure | 10 % | -2 % | 4 % | 10 % | Regulates its INLET by relieving downstream |

*SPE is the fractional outlet change per unit fractional inlet change.*

**A direct-acting spring regulator has a 20 to 25 percent wide outlet pressure band.** Every component downstream has to tolerate the whole band, and the relief valve has to be set above the top of it. If that band is unacceptable, the answer is a two-stage or dome-loaded regulator, not a tighter tolerance on the same device.

**Minimum inlet pressure.** A regulator needs a working differential. Below roughly 1.15 to 1.25 times the set pressure the poppet is fully open and the device has become a restriction. That is the lockup point for the upstream bottle and it determines how much pressurant is stranded: see [PressurizationAndBlowdown.md](PressurizationAndBlowdown.md).

**Dome-loaded regulators** deserve a note. Replacing the spring with a gas-filled dome gives a much flatter force-displacement characteristic, hence very low droop. It also makes the setpoint remotely adjustable by changing the dome pressure, which is why every serious test stand uses them. The cost is that the dome loading supply is itself a system that must be designed, and dome leakage changes the setpoint slowly and invisibly.

---

## Relief valves

A relief valve opens at its set pressure, reaches rated capacity at some **accumulation** above it, and recloses at a **reseat** pressure below it. The gap between set and reseat is the **blowdown**, and it exists to stop the valve chattering: without it, the valve would reclose the instant the pressure dropped by any amount and immediately reopen.

| Type | Accumulation | Blowdown | Kd | Notes |
|---|---|---|---|---|
| Spring relief | 10 % | 7 % | 0.87 | Back pressure shifts the set point. Not for manifolded discharge |
| Balanced bellows | 10 % | 7 % | 0.87 | Set point independent of back pressure. Bellows is fatigue limited |
| **Pilot operated** | **3 %** | **2 %** | 0.87 | Tight set point, operates to 98 % of set without leaking. Pilot failure disables it |

**Sizing:** the credible relieving case is almost always a **regulator failed fully open**. That is the dominant regulator failure mode and it is what the relief exists for. The relief must pass the flow the failed-open regulator delivers at maximum inlet pressure, not the normal system flow.

For choked gas:

```
A = mdot_relief / ( Kd * G_choked(P_set * (1 + accumulation), T) )
```

**Back pressure matters.** A conventional spring relief valve has the spring bonnet vented to atmosphere, so any back pressure on the outlet adds directly to the effective set pressure. Two conventional relief valves discharging into a shared manifold interfere with each other. That is what balanced bellows and pilot-operated designs solve.

---

## Burst discs

A burst disc is a one-shot rupture element. It opens fully and instantly, it never leaks before it bursts, and it does not reseat.

Three numbers characterize it and people usually quote only the first:

1. **Nominal burst pressure** at the reference temperature, usually 295 K
2. **Manufacturing tolerance**, typically +/- 5 to 10 percent. Down to 2 percent at a cost
3. **Temperature derate.** The disc material softens and the burst pressure falls

**Temperature derating** (fraction of the 295 K rating):

| Material | 373 K | 473 K | 673 K | 873 K |
|---|---|---|---|---|
| Aluminum | 0.85 | 0.70 (at 423 K) | -- | -- |
| Nickel | 0.93 | 0.80 | 0.62 (at 573 K) | -- |
| 316 stainless | 0.95 | 0.88 | 0.76 | -- |
| Monel | 0.96 | 0.90 | 0.78 | -- |
| **Inconel** | **0.97** | **0.92** | **0.82** | **0.66** |

A disc rated 10 MPa with a 10 percent tolerance, in aluminum at 423 K, bursts somewhere between 6.3 and 7.7 MPa. That is 30 percent below its nameplate and it has caught people out.

**The band matters in both directions.** The maximum of the band must be below the pressure that would damage the system (or it does not protect). The minimum of the band must be above the normal operating pressure (or it bursts as a nuisance and vents the system permanently).

**Burst disc plus relief valve in series** is a common architecture: the disc isolates the relief valve from the process (so the relief seat stays clean and does not leak) and the relief valve provides the reclosing capability. The interspace between them must be monitored, because a pinhole in the disc equalizes the interspace and the disc will then never burst at its rated pressure.

---

## The pressure set point ladder

Every pressure control chain has a ladder of set points that must be ordered with margin:

```
regulator outlet band maximum
    <  relief set pressure
    <  relief full flow pressure (set + accumulation)
    <  system MEOP
    <  burst disc minimum burst (rating - tolerance, derated for temperature)
    <  proof pressure
    <  burst pressure of the weakest component
```

**Two failure modes, both common:**

- **Relief set too close to regulator lockup.** The relief weeps or lifts during normal operation. On a spacecraft that vents the pressurant and ends the mission.
- **Burst disc minimum below relief full flow.** The disc bursts before the relief can do its reversible job, and the system is vented permanently by an event the relief was designed to handle.

`Regulator.checkPressureStackup()` evaluates the whole ladder and reports the margin at each step. A margin below 5 percent at any step is a finding: set point tolerances alone can consume that.

---

## Check valves

A check valve is a passive one-way valve. It has no command and no position feedback, which makes it the component most likely to be in an unknown state.

| Type | Crack [kPa] | K | Min flow fraction | Reverse leak [scc/s] | Close [ms] |
|---|---|---|---|---|---|
| **Poppet spring** | 20 | 3.0 | 0.25 | 1e-4 | 5 |
| Ball spring | 15 | 4.0 | 0.30 | 1e-3 | 8 |
| Swing | 2 | 2.0 | 0.40 | 1e-2 | 200 |
| Lift | 25 | 12.0 | 0.20 | 1e-4 | 10 |
| Duckbill | 3 | 5.0 | 0.10 | 1e-2 | 20 |
| **Dual poppet redundant** | 40 | 6.0 | 0.25 | **1e-6** | 5 |

### Chatter

**This is the failure mode that catches people.** The poppet is held open by the dynamic pressure of the flow acting against the spring. If the flow is too low, the poppet does not reach its stop and sits in an equilibrium position where any disturbance moves it. It then oscillates between the seat and its partially open position at the natural frequency of the spring-mass system, typically tens to hundreds of hertz.

Consequences, in the order they arrive:

1. Noise and a pressure oscillation that propagates into the system
2. Seat and poppet wear, delivered thousands of times per minute
3. Particle generation, which damages everything downstream
4. Seat failure, at which point the valve no longer checks

**A check valve sized for peak flow will chatter at low flow.** A system operating over a wide flow range needs the valve sized for the **minimum** flow, accepting more pressure drop at high flow, or a compliant element (a duckbill) that cannot chatter, or the check valve moved to a location where the flow is steady.

### Cracking pressure

```
dP = P_cracking + K * rho * V^2 / 2
```

At low flow the cracking pressure dominates completely, so a check valve in a low-flow line costs far more pressure than its `K` suggests. In the worked example below, the cracking pressure is 89 percent of the total loss.

### Reverse leakage and the pressurant manifold

The application that makes reverse leakage critical is a **common pressurant manifold feeding both a fuel tank and an oxidizer tank** through separate check valves. If either leaks, propellant vapor migrates back into the shared manifold. With a hypergolic pair, fuel vapor and oxidizer vapor meeting in the pressurant line react, deposit solids, and can ignite. **Vehicle losses have been attributed to exactly this mechanism.**

The design response is **series redundant check valves with a monitored interspace**: two valves in series with a pressure transducer between them, so a first failure is detectable before it becomes a second failure. That is what the `dual poppet redundant` type is and why it is standard for hypergolic pressurant isolation.

---

## Filters

A filter exists to protect something specific. Identify what, and it is almost always the smallest flow passage downstream.

**The rule:**

```
absolute rating  <=  smallest downstream passage / 10
```

A particle larger than about a third of a passage will lodge in it, so a ratio of 3 is the hard minimum. A ratio of 10 is the design target, and the margin covers particle agglomeration, non-spherical particles (a fibre passes a rating test then lodges), and filter degradation.

**Two ratings, and they are not the same thing:**

- **Nominal rating** is a marketing number with no agreed definition. It should not appear in a requirement.
- **Absolute rating** is defined by the beta ratio: upstream particle count over downstream count above the rated size. `efficiency = 1 - 1/beta`. Beta 1000 is 99.9 percent. **Aerospace practice calls beta 1000 "absolute"; much of industry calls beta 75 absolute.** State the beta value.

| Element | Permeability [m^2] | Dirt capacity [kg/m^2] | Area factor | Cleanable |
|---|---|---|---|---|
| Woven wire mesh | 2.0e-10 | 0.010 | 1 | yes |
| **Sintered wire mesh** | 8.0e-11 | 0.045 | 1 | yes |
| Sintered powder | 1.5e-11 | 0.080 | 1 | no |
| **Pleated mesh** | 8.0e-11 | 0.045 | **8** | yes |
| Etched disc | 3.0e-10 | 0.005 | 1 | yes |

**Sizing on pressure drop alone is wrong.** A clean metal element has a very low resistance, so sizing on dP produces a tiny element with a face velocity of metres per second and a dirt capacity in milligrams. It meets its pressure budget on day one and plugs almost immediately.

**Dirt capacity, and therefore life, is what actually sizes a filter:**

```
A = (contamination loading * volumetric flow * required life) / (dirt capacity per unit area)
```

Take the larger of the pressure-limited and life-limited areas.

**The first flush dominates the contamination load.** A newly assembled system sheds its own construction debris: weld spatter, machining chips, thread debris, blast media and whatever came off the inside of the tubing. That is why systems are flushed with a temporary coarse filter before the flight filter is installed, and why the flight filter goes in at the last possible assembly step.

**Do not over-filter.** A finer filter than necessary costs pressure drop, plugs sooner, and costs money without protecting anything additional.

---

## Cavitating venturis

A flow control device with no moving parts, no control loop and no power. See [Orifices.md](Orifices.md) for the physics; the summary:

```
mdot = Cd * At * sqrt( 2 * rho * (P1 - P_vapor) )
```

**Downstream pressure has no effect at all**, as long as the venturi stays choked. Put one in each branch of a feed system and the branches stop talking to each other: chamber pressure oscillations cannot propagate back, a valve slamming in one branch does not disturb the others, and the flow split is set by geometry rather than by relative downstream resistance. It is also a hydraulic fuse: if the chamber loses pressure the venturi does not let more propellant through.

**The costs are real.** A permanently spent pressure budget of 10 to 20 percent of upstream pressure, and a diffuser that has to survive continuous cavitation.

**The number that matters in operation is the unchoke margin.** If downstream pressure rises above the recovery limit the cavity collapses, the venturi silently becomes an ordinary venturi, and the flow becomes a function of downstream pressure again. **Nothing warns you; the flow just changes.**

| Diffuser | Recovery ratio P2/P1 at unchoke |
|---|---|
| Sharp expansion | 0.55 |
| Short diffuser (10 to 15 deg half angle) | 0.75 |
| **Standard diffuser (6 deg)** | **0.85** |
| Long diffuser (3 deg) | 0.92 |

Design for at least 10 percent of upstream pressure of unchoke margin. Chamber pressure rise during a burn, filter loading, and supply pressure decay over a blowdown all consume that margin in the same direction.

---

## Design rules of thumb

| Rule | Value | Why |
|---|---|---|
| Regulator outlet band | 20 to 25 % for direct acting | Everything downstream tolerates the whole band |
| Regulator SPE sign | Outlet RISES as supply falls | Counterintuitive; affects blowdown systems |
| Minimum regulator differential | 1.15 to 1.25 x set pressure | Below it the regulator is a restriction |
| Relief sizing case | Regulator failed fully open | Not the normal flow rate |
| Relief set above regulator lockup | > 10 % | Or it weeps during normal operation |
| Burst disc band | Nominal, tolerance AND temperature derate | The nameplate is not the burst pressure |
| Pressure ladder margin | > 5 % at every step | Set point tolerances consume less than that |
| Check valve sizing | For the MINIMUM flow | Chatter, not pressure drop, is the constraint |
| Check valve cracking pressure share | Can be 90 % of total dP at low flow | Do not size on K alone |
| Hypergolic pressurant isolation | Series redundant checks, monitored interspace | Vapor mixing has lost vehicles |
| Filter rating | <= passage / 10, hard minimum passage / 3 | Particles lodge above 1/3 |
| Filter sizing | On life, not on clean dP | A dP-sized element plugs immediately |
| Filter beta | State it. 1000 for aerospace absolute | Beta 75 and beta 1000 are both called "absolute" |
| Cavitating venturi unchoke margin | > 10 % of P1 | Three effects consume it in the same direction |

---

## Failure modes

**Regulator fails open.** The dominant regulator failure. Everything downstream sees the full supply pressure. This is what the relief valve exists for and it is why a regulator without a downstream relief is an incomplete design.

**Regulator creeps.** A slow rise in outlet pressure at zero flow, from a contaminated or damaged seat. It looks like nothing until the relief lifts.

**Relief valve fails to lift.** A seat that has been weeping and has galled or corroded shut. The relief was never tested because it never operated.

**Relief valve lifts during normal operation.** Set point too close to the operating band, or back pressure shifting the set point. On a spacecraft this ends the mission.

**Relief valve chatters.** Insufficient blowdown, or an oversized relief on a small system: the valve relieves faster than the system repressurizes, closes, reopens. Destroys the seat quickly.

**Burst disc bursts early.** Fatigue from pressure cycling, corrosion, or a temperature derate that was not applied. Discs have a cycle life; a disc in a cycling system needs a fatigue-rated design.

**Burst disc does not burst.** A pinhole equalized the interspace of a disc-plus-relief assembly, or the disc was installed backwards (reverse-buckling discs are directional and will hold far above rating in the wrong direction).

**Check valve chatters.** Covered above. Self-destructive.

**Check valve leaks backwards.** In a pressurant manifold, this allows propellant vapor mixing.

**Check valve installed backwards.** It happens, and there is often no functional test that catches it before the system is loaded. Mark and verify flow direction.

**Filter plugs.** Predictable if the life was calculated and surprising if it was not.

**Filter element collapses.** Reverse flow, or a plugged element with the full system differential across it. A collapsed element passes everything it had collected, all at once, downstream.

**Filter bypassed.** Some filter housings have a bypass relief that opens when the element plugs. That is correct for a lubrication system and catastrophic for a propulsion system: it dumps the collected contamination into exactly the passage the filter was protecting. **Do not use bypass filters in a propulsion system.**

**Cavitating venturi unchokes.** Silent loss of flow regulation.

---

## Operations

**Functional test every passive device at its actual differential.** A relief valve that lifts on a bench at 1 MPa may not lift at 1 MPa with 0.2 MPa of back pressure.

**Verify check valve direction after every installation.** Flow it and confirm.

**Instrument filters with a differential pressure gauge** and change them on measured dP, not on hours. The dP rise is highly nonlinear at the end of life and a time-based schedule either changes them too early or too late.

**Monitor the interspace** on any series-redundant check valve pair or disc-plus-relief assembly. The whole point of the redundancy is that the first failure is detectable.

**Record relief valve set point verification.** Relief valves drift, and a relief valve that has not been verified is not a relief valve.

**Flush new systems with a temporary coarse filter** before installing the flight element.

---

## Worked example

A regulated helium pressurization system: 30 MPa bottle blowing down to 3 MPa, 2.4 MPa regulated, 1 g/s rated flow, 3.5 MPa system MEOP, 5.25 MPa proof, 4.5 MPa Inconel burst disc at 5 percent tolerance.

**Regulator (direct acting spring):**

| Quantity | Value |
|---|---|
| Outlet at rated flow (droop) | 2.040 MPa |
| Outlet at lockup | 2.520 MPa |
| Outlet band including SPE | 2.040 to 2.585 MPa |
| **Band width** | **22.7 % of set** |
| Minimum inlet pressure | 2.880 MPa |
| Required Cv | 0.0220 |

The 22.7 percent band is flagged: everything downstream has to tolerate it. Note also that the final bottle pressure of 3.0 MPa is only just above the 2.88 MPa minimum differential, so the regulator loses control almost exactly when the bottle is considered empty. That is by design in this case, but it is worth confirming rather than discovering.

**Relief and burst disc:**

| Quantity | Value |
|---|---|
| Relief set (assumed 10 % above lockup) | 2.772 MPa |
| Relief full flow (10 % accumulation) | 3.049 MPa |
| Relief reseat (7 % blowdown) | 2.578 MPa |
| Relief area for 10 g/s | 4.054 mm^2 (2.27 mm equivalent diameter) |
| Burst disc band | 4.275 to 4.725 MPa |

**Pressure ladder check:**

| From | To | Margin | Status |
|---|---|---|---|
| Regulator outlet max 2.585 | Relief set 2.772 | +7.24 % | OK |
| Relief set 2.772 | Relief full flow 3.049 | +10.00 % | OK |
| Relief full flow 3.049 | System MEOP 3.500 | +14.78 % | OK |
| System MEOP 3.500 | Burst disc min 4.275 | +22.14 % | OK |
| Burst disc min 4.275 | Proof 5.250 | +22.81 % | OK |

The ladder closes, with the tightest margin (7.2 percent) between the regulator outlet maximum and the relief set pressure. That is the step to watch: any increase in regulator lockup or any downward drift of the relief set point closes it.

**Check valve** on the same manifold, dual poppet redundant, 4 mm port, 1 g/s design and 0.1 g/s minimum:

| Quantity | Value |
|---|---|
| Cracking pressure | 40.0 kPa |
| Dynamic pressure at design flow | 0.81 kPa |
| **Total forward dP** | **44.9 kPa** (89 % of it is cracking pressure) |
| Hold-open flow | 0.25 g/s |
| Chatter margin | 0.40 |
| **Chatter risk** | **SEVERE** |
| Reverse leak | 1e-6 scc/s He |

The chatter finding is the useful output: at 0.1 g/s minimum flow the poppet sits at 40 percent of its hold-open flow and will oscillate. The fix is to size the valve for 0.1 g/s rather than 1 g/s.

**Filter** protecting a 1.7 mm injector orifice, hydrazine at 45 g/s, 1 mg/L contamination, 10 hour life:

| Quantity | Value |
|---|---|
| Absolute rating (10:1 rule, rounded to standard) | 100 micron |
| Protection ratio | 17.0 |
| Pressure-limited area | 0.49 cm^2 |
| **Life-limited area** | **357 cm^2** |
| **Binding constraint** | **Life** |
| Envelope area (pleated, factor 8) | 44.6 cm^2 |
| Face velocity | 1.25 mm/s |
| Clean pressure drop | 9.1 Pa |
| Dirt capacity | 1.61 g |

The life constraint is 700 times the pressure constraint. That ratio is typical and it is why sizing a filter on pressure drop alone is a mistake.

Reproduce with:

```python
from Regulator import Regulator
from CheckValve import CheckValve
from Filter import Filter

regulator = Regulator()
regulator.setInputs({'fluid': 'Helium', 'regulatorType': 'direct acting spring',
                     'inletPressure': 30e6, 'finalInletPressure': 3.0e6,
                     'setPressure': 2.4e6, 'massFlow': 0.001, 'temperature': 293.15,
                     'burstDiscRating': 4.5e6, 'burstDiscMaterial': 'inconel',
                     'maximumOperatingPressure': 3.5e6, 'proofPressure': 5.25e6})
regulator.sizeRegulator()
regulator.sizeRelief(reliefFlow = 0.01)
regulator.checkBurstDisc()
regulator.checkPressureStackup()
print(regulator.generateReport())

check = CheckValve()
check.setInputs({'fluid': 'Helium', 'valveType': 'dual poppet redundant',
                 'nominalSize': 0.004, 'massFlow': 0.001, 'minimumMassFlow': 0.0001,
                 'upstreamPressure': 2.4e6})
check.calculatePressureDrop()
check.checkChatter()
print(check.compareTypes())

filterElement = Filter()
filterElement.setInputs({'fluid': 'N2H4', 'filterType': 'pleated mesh', 'massFlow': 0.045,
                         'upstreamPressure': 2.3e6, 'protectedPassage': 0.0017,
                         'allowableCleanPressureDrop': 2.0e4, 'contaminationLoading': 1e-3})
filterElement.selectRating()
filterElement.sizeElement(requiredLife = 36000.0)
print(filterElement.generateReport())
```

---

## Standards

| Standard | Scope |
|---|---|
| **NASA SP-8080** | Liquid rocket pressure regulators, relief valves, check valves, burst disks and explosive valves |
| ASME BPVC Section VIII Div. 1 UG-125 to UG-136 | Pressure relief devices |
| API 520 Part I / II | Sizing, selection and installation of pressure relieving devices |
| API 526 | Flanged steel pressure relief valves |
| API 527 | Seat tightness of pressure relief valves |
| ASME B16.34 | Valves, flanged, threaded and welding end |
| ISO 4126 | Safety devices for protection against excessive pressure |
| ISO 16889 | Hydraulic filters, multi-pass method for filtration performance (beta ratio) |
| ISO 4572 | Multi-pass method for evaluating filtration performance |
| SAE ARP4285 | Filter element performance |
| CGA S-1.3 | Pressure relief device standards, stationary storage containers |
| MIL-STD-1522 | Safe design and operation of pressurized missile and space systems |

---

## Tool interface

```python
from Regulator import Regulator        # regulator, relief valve, burst disc, pressure ladder
from CheckValve import CheckValve      # cracking pressure, chatter, reverse leakage
from Filter import Filter              # rating, area, clean dP, dirt capacity, life
from CavitatingVenturi import CavitatingVenturi   # choked liquid flow control
```

Key methods:

| Class | Methods |
|---|---|
| `Regulator` | `sizeRegulator`, `calculateOutletPressure`, `sizeRelief`, `checkBurstDisc`, `checkPressureStackup` |
| `CheckValve` | `calculatePressureDrop`, `checkChatter`, `calculateReverseLeakage`, `compareTypes` |
| `Filter` | `selectRating`, `sizeElement(requiredLife=...)`, `calculatePressureDrop`, `calculateLife` |
| `CavitatingVenturi` | `sizeThroat`, `calculateMassFlow`, `calculateUnchokeMargin` |

Lookup tables: `Regulator.REGULATOR_TYPES`, `Regulator.RELIEF_TYPES`, `Regulator.BURST_DISC_TEMPERATURE_DERATE`, `CheckValve.CHECK_VALVE_TYPES`, `Filter.FILTER_TYPES`, `Filter.BETA_RATIOS`, `CavitatingVenturi.DIFFUSER_RECOVERY`.

---

## References

1. NASA SP-8080, *Liquid Rocket Pressure Regulators, Relief Valves, Check Valves, Burst Disks, and Explosive Valves*, 1973. The single best reference on this topic.
2. API RP 520, *Sizing, Selection, and Installation of Pressure-Relieving Devices in Refineries*.
3. ASME BPVC Section VIII Division 1, *Rules for Construction of Pressure Vessels*.
4. ISO 16889, *Hydraulic fluid power -- Filters -- Multi-pass method for evaluating filtration performance of a filter element*.
5. Emerson Process Management, *Control Valve Handbook*, 5th ed., 2019.
6. Huzel, D. K. and Huang, D. H., *Modern Engineering for Design of Liquid-Propellant Rocket Engines*, AIAA, 1992.
7. Sutton, G. P. and Biblarz, O., *Rocket Propulsion Elements*, 9th ed., Wiley, 2016.
8. Crane Co., *Flow of Fluids Through Valves, Fittings, and Pipe*, Technical Paper No. 410.
