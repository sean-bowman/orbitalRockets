[Home](../README.md) > Chill-in and Conditioning

# Chill-in and Conditioning

## Contents

- [Overview](#overview)
- [The enthalpy balance](#the-enthalpy-balance)
- [Two bounds, and the band between them](#two-bounds-and-the-band-between-them)
- [Why hydrogen is a different problem](#why-hydrogen-is-a-different-problem)
- [Purge, and the thing that freezes](#purge-and-the-thing-that-freezes)
- [What it costs operationally](#what-it-costs-operationally)
- [Worked numbers](#worked-numbers)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Liquid oxygen poured into warm metal boils. It goes on boiling until the metal has given up its stored enthalpy, and until it stops the engine is being fed a two-phase mixture that no pump will tolerate and no injector was designed around.

Conditioning is the process of getting the hardware cold before the engine is asked to start. The propellant spent doing it is vented and lost.

---

## The enthalpy balance

The hardware has to give up

```
Q = m_metal * integral of cp(T) dT, from T_target to T_start
```

and the cryogen has to absorb it. Both halves have a subtlety.

**The metal's specific heat is not its room-temperature value**, and it is not a constant either. It falls steeply below about 100 K: 304 stainless is 470 J/(kg K) at room temperature and 248 at the liquid oxygen boiling point. A room-temperature figure over the whole range overstates the stored enthalpy by roughly a third.

**A single mean does not fix that, because the mean depends on where the range ends.** The same stainless line has an enthalpy-averaged specific heat of 413 J/(kg K) chilling for liquid methane and 331 chilling for liquid hydrogen, a spread of a quarter. **The material alone does not determine it and the cryogen has to be in the calculation**, which is why the integral above is written as an integral.

The curves are the NIST cryogenic material properties fits, in [common/cryogenicProperties.py](../../../common/cryogenicProperties.py), and the library integrates them over the range each chill-down actually traverses. Any mean it reports is the result of that integral rather than an input to it, so there is no table to drift.

**Two metals have no curve.** The NIST database carries thermal conductivity and linear expansion for Ti-6Al-4V and Inconel 718 and no specific heat, so those keep a constant mean and stay in the unvalidated register. The direction of that approximation is known: a constant quoted over the oxygen range never sees the collapse below 90 K, so it overstates a hydrogen chill-down by about 16 per cent.

**The cryogen's capacity depends on what the vapour does**, and that is where the whole problem lives.

---

## Two bounds, and the band between them

**The upper bound on mass** assumes the vapour leaves at its saturation temperature, so every kilogram absorbs only its latent heat. That is what happens when the flow is fast and the vapour is swept out before it can warm.

**The lower bound** assumes the vapour leaves at the metal's starting temperature, so every kilogram absorbs its latent heat plus the full sensible heating of the gas. That is what happens when the flow is slow enough for the vapour to stay in contact.

Real chill-down lies between them, and **the two bounds are the two chill-down methods**. The band is not an uncertainty in the calculation. It is the range the design decision actually spans.

For 45 kg of stainless conditioned from ambient:

| Cryogen | Latent heat | Vapour sensible | Lower bound | Upper bound | Band |
|---|---|---|---|---|---|
| LOX | 213 kJ/kg | 187 kJ/kg | 8.7 kg | 16.3 kg | 1.9 |
| LCH4 | 511 kJ/kg | 388 kJ/kg | 3.4 kg | 6.1 kg | 1.8 |
| LH2 | 449 kJ/kg | **3412 kJ/kg** | 1.2 kg | 10.5 kg | **8.6** |

---

## Why hydrogen is a different problem

Read the LH2 row again. Its latent heat is 449 kJ/kg and its vapour will absorb **3412 kJ/kg more** on the way back to ambient. Almost all of the cooling available is in the gas rather than in the phase change.

So for oxygen and methane the hardware mass decides the answer and the method only trims it, a band under two. **For hydrogen the method decides the answer**, a band of nearly nine.

That single ratio is why the liquid hydrogen chill-down literature is entirely about trickle against pulse flow scheduling, optimising for minimum propellant or minimum time, and the liquid oxygen literature is not. It is not that hydrogen researchers are more thorough. It is that with hydrogen there is a factor of nine on the table and with oxygen there is a factor of two.

---

## Purge, and the thing that freezes

Before any cryogen enters, the hardware is purged, and the two sides are purged with different gases for a reason worth knowing.

The RS-25 purges its **oxidiser side with dry nitrogen** to eliminate moisture, and its **fuel side with dry helium** to eliminate air as well as moisture. Nitrogen is fine against liquid oxygen at 90 K. Against liquid hydrogen at 20 K it is a solid.

The same source puts it plainly: liquid hydrogen is cold enough to freeze air into a solid block of ice. **Helium is the only purge gas that stays a gas at hydrogen temperature**, and that is the whole reason helium appears in a hydrogen engine's ground support at all.

---

## What it costs operationally

Conditioning is not a fast process. The RS-25 maintains small recirculation flows for an hour or more to chill its four turbopumps to cryogenic temperature and eliminate gas pockets in the feed system, and takes a final helium purge about four minutes before the start command.

Against that, the reference booster in this repository burns **RP-1, which is stored at ambient and needs no conditioning at all**. Only the oxidiser side is cryogenic.

Half the operational simplicity of a kerosene booster is in that sentence, and it is a real part of why kerosene persists on first stages long after its specific impulse stopped being competitive.

---

## Worked numbers

45 kg of stainless 304, the oxidiser side of the reference booster, conditioned from 293 K.

| Quantity | Value |
|---|---|
| Metal enthalpy to remove, to LOX temperature | 3.56 MJ |
| Effective specific heat, integrated, to LOX | 400 J/(kg K) |
| Effective specific heat, same metal, to LH2 | 331 J/(kg K) |
| LOX required, lower bound | 8.9 kg |
| LOX required, upper bound | 16.7 kg |
| Band | 1.9 to one |
| Same hardware with LH2, band | 8.6 to one |

---

## Design rules of thumb

- **Integrate the specific heat over the range, do not take a value at a temperature.** A room-temperature value errs by a third in the unsafe direction, and even the midpoint value errs by three per cent in the same direction because the curve is concave here.
- **A mean specific heat belongs to a range, not to a metal.** Quoting one without the range it was integrated over is how the hydrogen case gets a number 16 per cent too large.
- **Quote a band, not a number.** The method spans it and stating a single figure hides the design decision.
- **For hydrogen, design the schedule.** It is worth a factor of nine and nothing else on the system is.
- **Helium on the hydrogen side.** Nitrogen freezes.
- **Count the conditioning propellant in the mass budget.** It is loaded, it is vented, and it is not available for the mission.

---

## Failure modes

**Room-temperature specific heat.** Overstates the required cryogen by a third or more.

**A mean specific heat carried across cryogens.** It is a property of the range, not of the metal, and the four cryogens span a quarter on the same line.

**A single-number chill-down estimate.** Hides a factor of nine on hydrogen.

**Nitrogen purge on a hydrogen system.** It solidifies and blocks what it was meant to clear.

**Starting before the pumps are conditioned.** Two-phase flow into a pump is cavitation with no NPSH margin to trade; see [turbomachinery](../../turbomachinery/docs/CavitationAndNPSH.md).

**Treating chill-down as a ground operation only.** An engine that restarts in flight has to re-condition, and there may be no recirculation available to do it with.

---

## Tool interface

```python
from ChillDown import ChillDown

chill = ChillDown()
chill.setInputs({'cryogen':   'LOX',
                 'material':  'stainless 304',
                 'metalMass': 45.0})

result     = chill.calculateMass()
comparison = chill.compareCryogens(['LOX', 'LCH4', 'LH2'])

print(chill.generateReport())
```

Latent heat and vapour sensible heat both come from the equation of state through the shared property wrapper, so nothing in the calculation is a tabulated value that could go stale.

---

## References

- Biggs, *Space Shuttle Main Engine: The First Ten Years*, part 3, Start and Shutdown, AAS History Series volume 13
- NASA Glenn liquid hydrogen line chilldown experiments, trickle and pulse method comparisons
- Darr and Hartwig, liquid hydrogen boiling heat transfer correlations
- Barron, *Cryogenic Systems*
