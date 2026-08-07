[Home](../../README.md) > Pressurization and Blowdown

# Pressurization and Blowdown

## Contents

- [Overview](#overview)
- [Architectures](#architectures)
- [Regulated system sizing](#regulated-system-sizing)
- [Blowdown system sizing](#blowdown-system-sizing)
- [Pressurant selection](#pressurant-selection)
- [Real gas effects](#real-gas-effects)
- [Ullage collapse](#ullage-collapse)
- [Autogenous and heated pressurization](#autogenous-and-heated-pressurization)
- [Propellant management](#propellant-management)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked example](#worked-example)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Every pressure-fed system has to answer one question: how much pressurant, in how big a bottle, at what pressure. The answer determines a surprising fraction of the dry mass of a small spacecraft, because a composite overwrapped pressure vessel at 30 MPa is heavy and the gas inside it is not.

The chain runs: **feed system pressure drop -> required tank pressure -> tank wall thickness -> tank mass**, and separately **required tank pressure -> pressurant mass -> bottle mass**. Both branches make the case for keeping the tank pressure as low as the feed system will allow, which is the argument for spending effort on line sizing.

---

## Architectures

| Architecture | Pressurant source | Thrust profile | Complexity |
|---|---|---|---|
| **Regulated** | High pressure bottle plus regulator | Constant | Regulator, bottle, isolation valves, relief |
| **Blowdown** | Tank charged once at loading | Falls with tank pressure | None beyond the tank |
| **Autogenous** | Vaporized propellant | Constant (regulated) | Heat exchanger, but no separate gas |
| **Pump fed** | Turbopump | Constant | Entirely different problem |

**Regulated.** A high pressure bottle feeds a regulator which holds the propellant tank at constant pressure. Thrust is constant over the whole burn, the propellant tank is sized for the regulated pressure only, and the cost is a regulator (a single point failure with a well-documented failure mode), a high pressure bottle, isolation valves, and relief protection downstream of the regulator.

**Blowdown.** The propellant tank is charged with pressurant once, at loading, and the pressure falls as propellant is consumed. No regulator, no separate bottle, no isolation valves. The cost is that thrust falls with pressure, and that the propellant tank has to be sized for the initial pressure and large enough to hold the initial ullage as well as the propellant.

**For a small satellite the blowdown system wins on almost every axis except performance**, which is why it is the default for spacecraft attitude control. For anything with a demanding thrust or mixture ratio requirement, the regulated system wins.

---

## Regulated system sizing

**Ullage requirement.** As propellant leaves, the ullage must be filled with gas at the regulated pressure. Work the energy balance on the ullage control volume with adiabatic tank walls:

```
m_in * h_supply = U_final + P_tank * V        (the P*V term is the work done expelling propellant)
m * cv * T_f    = m * cp * T_s - m * R * T_f
cp * T_f        = cp * T_s      ->      T_f = T_s
```

The final ullage temperature equals the **supply** temperature, which is a slightly surprising result and it makes the ideal requirement simply

```
m_ullage = rho(P_tank, T_supply) * V_propellant
```

**Bottle sizing.** The bottle must hold that plus a residual, because the regulator stops working when the bottle pressure falls to its lockup point:

```
V_bottle = m_required / ( rho(P_initial, T_initial) - rho(P_lockup, T_final) )
```

For an **isothermal** discharge `T_final = T_initial`. For an **adiabatic** discharge the bottle cools as it empties:

```
T_final = T_initial * (P_lockup / P_initial)^((gamma-1)/gamma)
```

and the residual density is higher, so more gas is stranded. The isothermal case is the optimistic bound and the adiabatic case the conservative one; a real bottle is between them and closer to isothermal for a slow spacecraft expulsion over months.

**The usable mass fraction** is the number to watch. For a 30 MPa bottle regulated to 2.4 MPa with a 2.88 MPa lockup, roughly 89 percent of the loaded gas is usable and 11 percent is stranded. Lowering the regulated pressure or raising the bottle pressure both improve it.

---

## Blowdown system sizing

The ullage gas expands polytropically as propellant leaves:

```
P_i * V_i^n = P_f * V_f^n,      V_f = V_i + V_propellant
V_i = V_propellant / ( B^(1/n) - 1 ),      B = P_i / P_f
```

| Blowdown ratio B | Initial ullage / propellant volume | Tank oversizing | Final thrust |
|---|---|---|---|
| 2:1 | 100 % | 2.00x | 50 % |
| 3:1 | 50 % | 1.50x | 33 % |
| **4:1** | **33 %** | **1.33x** | **25 %** |
| 5:1 | 25 % | 1.25x | 20 % |
| 10:1 | 11 % | 1.11x | 10 % |

**4:1 is close to universal** because it balances two costs that move in opposite directions: a lower ratio needs a bigger tank, and a higher ratio delivers a wider thrust range that the control system has to tolerate.

`n = 1.0` is isothermal, correct for a slow spacecraft expulsion over months where the gas stays in equilibrium with the tank wall. `n = gamma` is adiabatic, correct for a fast expulsion, and it requires **more** initial ullage for the same blowdown ratio because the gas cools as it expands and loses pressure faster.

**The tank must be sized for the initial pressure**, which is `B` times the final pressure. That is the hidden cost: a 4:1 blowdown tank at 2.4 MPa initial carries a wall sized for 2.4 MPa, while a regulated system delivering the same 0.6 MPa final would need a wall for only 0.6 MPa plus margin. In practice a regulated system runs at constant pressure so the comparison is not quite that stark, but the blowdown tank is always the more heavily loaded one.

---

## Pressurant selection

| Gas | Molar mass [g/mol] | Mass for the same P-V | Notes |
|---|---|---|---|
| **Helium** | 4.003 | **1.0** | One seventh the mass of nitrogen. Leaks and permeates through everything. Expensive |
| Nitrogen | 28.013 | 7.0 | Cheap and available. Dissolves in hydrazine and hydrocarbons. Liquefies at 77 K |
| Argon | 39.948 | 10.0 | Heaviest. Used where inertness with an exotic propellant matters more than mass |

**The molar mass column is the whole story for a flight system.** Pressurant mass scales directly with molar mass at a given pressure and volume, so helium costs one seventh the mass of nitrogen for the same job. That is decisive for flight and irrelevant for a ground system, which is why test stands run on GN2 and vehicles run on GHe.

**Solubility matters more than people expect.** Nitrogen dissolves appreciably in hydrazine and in hydrocarbons. Dissolved pressurant comes out of solution when the pressure drops, which is exactly what happens in the feed line and at the injector. The result is gas in the propellant, flow instability and injector maldistribution. Helium is much less soluble, which is a second reason it is preferred.

**Nitrogen liquefies at 77 K**, so it cannot pressurize a tank colder than that, which rules it out for LH2 and marginal for LN2 and LOX.

---

## Real gas effects

**Helium at 30 MPa and 293 K has a compressibility factor of about 1.14.** Treating it as an ideal gas under-predicts the stored mass by 14 percent, and that error goes directly into the bottle volume and therefore into the vehicle dry mass.

| Gas | P [MPa] | T [K] | Z |
|---|---|---|---|
| Helium | 20 | 293 | 1.10 |
| **Helium** | **30** | **293** | **1.14** |
| Helium | 45 | 293 | 1.21 |
| Nitrogen | 30 | 293 | 1.14 |
| Argon | 30 | 293 | 0.99 |

Note that argon at 30 MPa is essentially ideal (`Z = 0.99`) because its attractive and repulsive departures nearly cancel at that state, while helium is strongly non-ideal in the repulsive direction at the same pressure. The sign is not intuitive and it is a good reason to use a real property backend rather than a rule of thumb. The [`Pressurization`](../Pressurization.py) class uses `fluidProps` throughout for exactly this reason.

---

## Ullage collapse

The ideal calculation assumes the ullage gas neither gains nor loses heat. In reality it loses heat to the tank wall and to the cold propellant surface, its temperature falls, its density rises, and **more mass is needed to hold the same pressure**. That is ullage collapse.

| Duty | Collapse factor |
|---|---|
| Ideal (no heat transfer) | 1.00 |
| Storable, fast expulsion (minutes) | 1.10 |
| **Storable, spacecraft duty (long, many small expulsions)** | **1.15** |
| Storable, slow expulsion (hours) | 1.25 |
| Cryogenic, fast expulsion | 1.35 |
| Cryogenic, slow expulsion | **1.60** |

**It is the largest single correction in pressurant sizing.** A cryogenic slow expulsion needs 60 percent more pressurant than the ideal calculation says, and a design that omitted it runs out of pressurant before it runs out of propellant.

The mechanism is worth understanding: the pressurant enters hot, contacts a tank wall and a liquid surface that are both far colder, and gives up heat to both. Condensation of the pressurant is not usually the issue (helium does not condense); the issue is simple sensible cooling of the gas.

**Diffusers** at the pressurant inlet exist to manage this. A pressurant inlet that jets directly at the liquid surface maximizes the heat transfer and the collapse; a diffuser that spreads the gas gently across the ullage minimizes it. A well-designed diffuser can move a collapse factor from 1.5 to 1.2 for no mass.

---

## Autogenous and heated pressurization

**Autogenous pressurization** uses vaporized propellant as its own pressurant. Tap liquid from the tank, run it through a heat exchanger (usually on the engine), and return it as gas to the ullage.

Advantages:

- No separate pressurant, no bottle, no bottle mass
- No dissolved-gas problem, because the gas is the propellant
- No compatibility question

Disadvantages:

- Needs a heat source, which means engine operation, so it cannot pressurize before start
- The heat exchanger is a component with its own failure modes
- The ullage is now saturated propellant vapor, which condenses on the cold wall and on the liquid surface, so the collapse factor is much worse
- Only works for a propellant that can be vaporized usefully; it is standard for LOX and LCH4 and LH2, and not used for storables

**Heated helium** is the intermediate: helium from a bottle, warmed by a heat exchanger before it enters the tank. Warmer gas is less dense, so less mass is required for the same volume. A 293 K to 500 K heat exchanger reduces the pressurant mass requirement by roughly 40 percent, which for a large vehicle is a substantial saving that pays for the heat exchanger.

---

## Propellant management

In zero gravity the liquid does not sit at the bottom of the tank, which creates a problem: the pressurant outlet and the propellant outlet must each stay on the correct side of the interface.

| Device | How it works | Notes |
|---|---|---|
| **Surface tension PMD** | Vanes and sponges hold liquid over the outlet by capillary action | No moving parts, no life limit, no compatibility question. The spacecraft standard. Limited acceleration capability |
| **Diaphragm** | An elastomer or metal diaphragm separates gas from liquid | Positive expulsion, works under any acceleration. Elastomer compatibility and permeation limits; metal diaphragms have a limited number of reversals |
| **Bladder** | A flexible bag holds the propellant | Similar to a diaphragm; folding fatigue is the life limit |
| **Piston** | A sliding piston with a seal | Positive expulsion, but the seal is a leak path between gas and propellant |
| **Settling burn** | A small thrust settles the propellant before the main burn | No hardware in the tank, but it costs propellant and time |

**Expulsion efficiency** is the fraction of loaded propellant that can actually be delivered. It is typically 97 to 99.5 percent for a well-designed PMD and essentially 100 percent for a diaphragm. The residual is unusable mass carried for the whole mission.

---

## Design rules of thumb

| Rule | Value | Why |
|---|---|---|
| Blowdown ratio | 4:1 | Balances tank oversizing against thrust range |
| Blowdown initial ullage | `V_prop / (B - 1)` for isothermal | 33 % at 4:1 |
| Regulated usable mass fraction | 85 to 92 % | The rest is stranded at regulator lockup |
| Pressurant | Helium for flight, nitrogen for ground | 7:1 mass ratio |
| Real gas Z for He at 30 MPa | 1.14 | Ideal gas is 14 % wrong on stored mass |
| Collapse factor, storable | 1.10 to 1.25 | The largest correction in the calculation |
| Collapse factor, cryogenic | 1.35 to 1.60 | Cold liquid surface cools the ullage hard |
| Use a diffuser at the pressurant inlet | Always | Can move the collapse factor by 0.3 for no mass |
| Heated helium saving | ~40 % pressurant mass for 293 to 500 K | Pays for the heat exchanger on a large vehicle |
| Nitrogen minimum tank temperature | > 130 K | It liquefies at 77 K |
| Expulsion efficiency | 97 to 99.5 % with a PMD | The residual is dead mass |
| Relief downstream of every regulator | Always | The regulator fails open |

---

## Failure modes

**Regulator fails open.** Everything downstream sees full bottle pressure. This is why the relief valve exists. See [FlowControlDevices.md](FlowControlDevices.md).

**Pressurant runs out before propellant.** From an unaccounted collapse factor, an underestimated residual, or a leak. The propellant that remains is unusable.

**Dissolved pressurant coming out of solution.** Nitrogen in hydrazine or in a hydrocarbon. Gas appears in the feed line downstream of the tank, and the injector sees a two-phase flow.

**Ullage collapse worse than designed.** Usually from a pressurant inlet that jets at the liquid surface rather than diffusing.

**Tank overpressure during loading.** The tank is pressurized before the propellant is loaded, or the vent path is closed during a thermal excursion. The relief protection has to cover the ground operations case, not just flight.

**Propellant migration into the pressurant line.** Through a leaking check valve, or by boiling back up the line. In a common-manifold hypergolic system this is a vehicle-loss mechanism.

**Blowdown tank sized for the final pressure.** A design error rather than a failure, but a common one: the tank must hold the **initial** pressure.

**PMD failure to retain.** A surface tension device exceeded by an acceleration it was not designed for. The outlet gulps gas and the engine sees a pressurant slug.

---

## Worked example

A 30 L hydrazine load at 2.4 MPa tank pressure, 293.15 K, helium pressurant.

**Blowdown at 4:1 isothermal:**

| Quantity | Value |
|---|---|
| Blowdown ratio | 4.0 |
| Final tank pressure | 0.600 MPa |
| **Initial ullage volume** | **10.0 L** |
| Total tank volume | 40.0 L |
| Initial ullage fraction | 25.0 % |
| Tank oversizing | 1.333x propellant volume |
| Helium density at 2.4 MPa, 293 K | 3.896 kg/m^3 |
| Compressibility factor | 1.012 |
| **Pressurant mass** | **0.0390 kg** |

**Regulated from a 30 MPa bottle, spacecraft duty collapse factor 1.15:**

| Quantity | Value |
|---|---|
| Tank gas density | 3.896 kg/m^3 |
| Ideal ullage mass | 0.1169 kg |
| Collapse factor | 1.15 |
| **Usable pressurant required** | **0.1344 kg** |
| Bottle initial density (30 MPa, Z = 1.14) | 43.166 kg/m^3 |
| Regulator lockup (assumed 1.2x set) | 2.880 MPa |
| Bottle final density | 4.664 kg/m^3 |
| **Bottle volume** | **3.49 L** |
| Total loaded pressurant | 0.1507 kg |
| Residual at lockup | 0.0163 kg |
| **Usable mass fraction** | **89.2 %** |

**The comparison is instructive.** The regulated system needs 0.151 kg of helium in a 3.5 L bottle, against 0.039 kg for the blowdown. But the blowdown system needs a 40 L tank instead of a 30 L one, and the extra 10 L of tank wall almost certainly weighs more than the 0.11 kg of extra helium plus the 3.5 L bottle. The trade is real and it has to be run with actual tank mass numbers, not with pressurant mass alone.

**Pressurant comparison at the regulated condition:**

| Gas | MW [g/mol] | Mass [kg] | Bottle [L] | Z |
|---|---|---|---|---|
| **Helium** | 4.003 | **0.151** | 3.49 | 1.141 |
| Nitrogen | 28.013 | 1.074 | 3.55 | 1.140 |
| Argon | 39.948 | 1.526 | 3.06 | 0.987 |

Nitrogen costs 0.92 kg more than helium for a nearly identical bottle volume. On a small spacecraft that is a decisive difference.

Reproduce with:

```python
from Pressurization import Pressurization

blowdown = Pressurization()
blowdown.setInputs({'architecture': 'blowdown', 'pressurant': 'helium',
                    'propellantVolume': 0.030, 'tankPressure': 2.4e6,
                    'blowdownRatio': 4.0, 'tankTemperature': 293.15,
                    'polytropicExponent': 1.0})
blowdown.calculateBlowdown()
print(blowdown.generateReport())

regulated = Pressurization()
regulated.setInputs({'architecture': 'regulated', 'pressurant': 'helium',
                     'propellantVolume': 0.030, 'tankPressure': 2.4e6,
                     'tankTemperature': 293.15, 'bottlePressure': 30e6,
                     'bottleTemperature': 293.15, 'bottleProcess': 'isothermal',
                     'collapseFactorKey': 'storable, spacecraft duty'})
regulated.calculateRegulated()
print(regulated.generateReport())
print(regulated.comparePressurants())
```

---

## Standards

| Standard | Scope |
|---|---|
| **NASA SP-8080** | Liquid rocket propellant tank pressurization |
| NASA SP-8109 | Liquid rocket engine centrifugal flow turbopumps (for the pump-fed alternative) |
| **AIAA S-080** | Space systems metallic pressure vessels, pressurized structures and pressure components |
| **AIAA S-081** | Space systems composite overwrapped pressure vessels |
| ASME BPVC Section VIII | Pressure vessels |
| NASA-STD-8719.17 | Ground-based pressure vessels and pressurized systems |
| MIL-STD-1522 | Safe design and operation of pressurized missile and space systems |
| ISO 14623 | Space systems, pressure vessels and pressurized structures |
| ECSS-E-ST-32-02 | Structural design and verification of pressurized hardware |

---

## Tool interface

```python
from Pressurization import Pressurization

system = Pressurization()
system.setInputs({'architecture': 'regulated', 'pressurant': 'helium',
                  'propellantVolume': 0.030, 'tankPressure': 2.4e6,
                  'tankTemperature': 293.15, 'bottlePressure': 30e6,
                  'regulatorLockupPressure': 2.88e6,
                  'collapseFactorKey': 'storable, spacecraft duty',
                  'bottleProcess': 'isothermal'})

system.calculateRegulated()      # pressurant mass, bottle volume, residual, usable fraction
system.calculateBlowdown()       # ullage volume, tank oversizing (set architecture first)
system.comparePressurants()      # He vs N2 vs Ar at these conditions
print(system.generateReport())
```

Lookup tables: `Pressurization.PRESSURANT_GASES`, `Pressurization.COLLAPSE_FACTORS`, `Pressurization.BOTTLE_PROCESSES`.

The downstream consequences are in [`Regulator`](../Regulator.py) (pressure control and the set point ladder) and [`MonopropThruster.calculateBlowdown`](../MonopropThruster.py) (the thrust decay).

---

## References

1. NASA SP-8080, *Liquid Rocket Propellant Tank Pressurization*, 1975.
2. Sutton, G. P. and Biblarz, O., *Rocket Propulsion Elements*, 9th ed., Wiley, 2016.
3. Huzel, D. K. and Huang, D. H., *Modern Engineering for Design of Liquid-Propellant Rocket Engines*, AIAA, 1992.
4. Van Dresar, N. T., "Prediction of Pressurant Mass Requirements for Axisymmetric Liquid Hydrogen Tanks", *Journal of Propulsion and Power*, Vol. 13, No. 6, 1997.
5. Jaekle, D. E., "Propellant Management Device Conceptual Design and Analysis", AIAA 91-2172 and the subsequent series on vanes, sponges, traps and troughs.
6. AIAA S-080A-2018, *Space Systems -- Metallic Pressure Vessels, Pressurized Structures, and Pressure Components*.
7. Barron, R. F., *Cryogenic Systems*, 2nd ed., Oxford University Press, 1985.
