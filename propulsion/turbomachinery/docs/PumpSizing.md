[Home](../README.md) > Pump Sizing

# Pump Sizing

## Contents

- [Overview](#overview)
- [Specific speed decides what you are building](#specific-speed-decides-what-you-are-building)
- [Staging is the lever](#staging-is-the-lever)
- [Tip speed is a materials limit](#tip-speed-is-a-materials-limit)
- [Efficiency, and why rocket pumps look bad](#efficiency-and-why-rocket-pumps-look-bad)
- [Validation, and the input that decides it](#validation-and-the-input-that-decides-it)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Worked numbers](#worked-numbers)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

A rocket pump is an ordinary centrifugal pump asked to do something extreme, and nearly everything difficult about it follows from one ratio: **the head is enormous and the flow is not.**

That single fact puts the specific speed far below where pump efficiency peaks, puts the required tip speed against a materials limit, and forces multiple stages on anything pumping hydrogen. None of those are separate problems.

---

## Specific speed decides what you are building

```
Omega_s = omega sqrt(Q) / (g H)^0.75
```

with `omega` in rad/s, `Q` in m^3/s and `H` in metres. **Compute it first**, before any dimension exists, because it is a shape parameter: two pumps with the same specific speed have geometrically similar impellers regardless of size, fluid or speed.

| `Omega_s` | Geometry | Character |
|---|---|---|
| 0.20 to 0.80 | Radial | High head, low flow. Where nearly every rocket pump sits |
| 0.80 to 2.20 | Mixed flow | The middle ground |
| 2.20 to 5.50 | Axial | High flow, low head |

The literature is overwhelmingly in US customary specific speed, `N[rpm] sqrt(Q[gpm]) / H[ft]^0.75`, and the conversion is **2733** times the dimensionless value. That factor was verified numerically against a hand-computed case rather than taken on trust.

The worked example fuel pump comes out at 0.256 dimensionless, 701 US customary, which is radial and near the bottom of the radial band.

**A caution that the RS-25 low pressure fuel turbopump makes concrete.** That machine runs at a dimensionless specific speed of about 0.285, where the classical industrial chart says radial, and the real pump is **axial**. A rocket boost pump is axial because it is chosen for cavitation performance, and an axial inducer stage tolerates far more vapour than a radial impeller. That is a rocket practice reason rather than a specific speed one, and reading the industrial chart across gets it wrong. See [CavitationAndNPSH](CavitationAndNPSH.md).

---

## Staging is the lever

Specific speed goes as `H^-0.75`, so splitting the head across `n` stages multiplies the per-stage specific speed by `n^0.75`.

| Stages | Per-stage `Omega_s` | Multiplier |
|---|---|---|
| 1 | 0.179 | 1.00 |
| 2 | 0.302 | 1.68 |
| 3 | 0.409 | 2.28 |
| 4 | 0.507 | 2.83 |

**That is why a hydrogen pump has several stages and a kerosene pump has one.** Hydrogen at 71 kg/m^3 needs an enormous head in metres for the same pressure rise, which drives the single-stage specific speed to a value where nothing works well.

Staging is not primarily about tip speed, though it helps there too. It is about moving the specific speed back into a range where an impeller can be efficient.

---

## Tip speed is a materials limit

```
U = sqrt(g H / psi)
```

with `psi` the head coefficient, `g H / U^2`. A backswept centrifugal impeller reaches 0.45 to 0.60; above that the blade loading is impractical.

The impeller is a rotating disc carrying its own centrifugal load, so the limit is a hoop stress problem:

| Material | Tip speed limit [m/s] |
|---|---|
| Aluminium | 350 |
| Monel K-500 | 450 |
| Titanium | 550 |
| Inconel 718 | 600 |

**Head goes as the square of tip speed, so the stage count goes as the square of the overrun.** A pump fifty per cent over the limit needs three stages, not two. That is not obvious and it is worth stating.

Monel appears on the list because LOX compatibility frequently decides the material before strength does, and it costs 100 m/s against titanium.

---

## Efficiency, and why rocket pumps look bad

Efficiency peaks near a specific speed of one and falls away below it, which is exactly where rocket pumps are forced to operate. The worked example fuel pump reaches 65 per cent against a peak of 85.

**That is structural rather than a sign of poor design.** A pump asked for high head at low flow cannot be efficient, and no amount of development changes the specific speed.

The efficiency correlation in this library is a fit to the range rocket pumps actually run in, roughly 0.2 to 0.4 dimensionless, rather than a fit to data. **It is a ranking tool and it is registered as unvalidated.** What it captures correctly is the direction and the rough magnitude; what it must not be used for is predicting a specific machine.

---

## Validation, and the input that decides it

Checked against the RS-25 high pressure fuel turbopump, which publishes shaft speed and shaft power together and therefore closes the loop on a pump model.

| Stages assumed | Predicted shaft power [MW] | Published [MW] | Error |
|---|---|---|---|
| 1 | 77.3 | 51.45 | **+50 %** |
| 2 | 61.6 | 51.45 | +20 % |
| **3, as published** | **56.0** | **51.45** | **+9 %** |
| 4 | 53.2 | 51.45 | +3 % |

**Nine per cent high at the correct stage count is good agreement for a first order model, and the direction is right: it is conservative.**

The important result is the first row. **A three stage pump treated as one stage overpredicts the shaft power by half, and the answer looks entirely plausible.** The model is not wrong; it is sensitive to an input that is easy to omit, and the omission produces a number nothing in the output flags.

The implied real efficiency of the HPFTP is 82 per cent against the library's 75 at three stages, so the correlation is seven points conservative on a best-in-class machine.

---

## Design rules of thumb

- **Compute specific speed before anything else.** It decides the machine.
- **Always state the stage count.** A multi-stage pump analysed as single stage is wrong by half.
- **Use per-stage specific speed for efficiency**, never the overall value.
- **Stage a hydrogen pump.** The density leaves no choice.
- **Check tip speed against the material**, and remember the stage count goes as the square of the overrun.
- **Let LOX compatibility pick the material first**, then live with the tip speed it allows.
- **Do not read the industrial geometry chart across to a boost pump.** Rocket boost pumps are axial for cavitation reasons.

---

## Failure modes

**Stage count omitted.** Fifty per cent error in shaft power, and the turbine is then sized from it.

**Overall specific speed used for efficiency on a multi-stage pump.** The same error by a different route.

**A single stage assumed for hydrogen.** The specific speed lands somewhere nothing works.

**Tip speed checked and the stage count not recomputed.** Head goes as the square of tip speed, so the two are not independent.

**The industrial geometry chart applied to a boost pump.** Says radial, the real machine is axial.

**The efficiency correlation used to predict rather than rank.** It is a fit to a range, not to data.

---

## Worked numbers

The worked example fuel pump: RP-1, 10.34 kg/s, 12.5 MPa rise, 30 000 rpm.

| Quantity | Value |
|---|---|
| Head | 1574 m |
| Volumetric flow | 12.77 l/s |
| Specific speed | 0.256 dimensionless, 701 US |
| Geometry | Radial |
| Stages | 1 |
| Tip speed | 168 m/s against a 550 m/s limit |
| Impeller diameter | 106.6 mm |
| Efficiency | 65 % |
| Shaft power | 0.298 MW |
| Bearing DN | 1.12 million against a 2.0 million limit |

RS-25 HPFTP validation: LH2, 73.1 kg/s, 41 MPa, 35 360 rpm, 3 stages.

| Quantity | Value |
|---|---|
| Hydraulic power | 42.2 MW |
| Published shaft power | 51.45 MW |
| Implied real efficiency | 82 % |
| Library efficiency at 3 stages | 75 % |
| Library shaft power | 56.0 MW, +9 % |

---

## Standards

| Standard | What it gives you |
|---|---|
| **NASA SP-8107** | **Turbopump systems for liquid rocket engines.** The design monograph |
| NASA SP-8109 | Liquid rocket engine centrifugal flow turbopumps |
| NASA SP-125 | Design of liquid propellant rocket engines, the turbopump chapters |
| Stepanoff, *Centrifugal and Axial Flow Pumps* | The specific speed machinery |

---

## Tool interface

```python
from Pump import Pump

pump = Pump()
pump.setInputs({'propellant':       'RP-1',
                'density':          810.0,
                'massFlow':         10.34,
                'pressureRise':     12.5e6,
                'shaftSpeed':       30000.0,
                'impellerMaterial': 'titanium',
                'stages':           1})

similarity = pump.calculateSpecificSpeed()
print(similarity['specificSpeed'], similarity['usSpecificSpeed'], similarity['geometry'])

impeller = pump.sizeImpeller()
print(impeller['tipSpeed'], impeller['requiredStages'], impeller['dnNumber'])

print(pump.calculatePower()['shaftPower'])
```

Omitting `stages` lets the class choose whatever the tip speed limit requires, which is safer than defaulting to one.

---

## References

- NASA SP-8107, *Turbopump systems for liquid rocket engines*
- NASA SP-8109, *Liquid rocket engine centrifugal flow turbopumps*
- Huzel and Huang, *Modern Engineering for Design of Liquid Propellant Rocket Engines*
- Stepanoff, *Centrifugal and Axial Flow Pumps*
- Sutton and Biblarz, *Rocket Propulsion Elements*, chapter 10
