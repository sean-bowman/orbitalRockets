[Home](../README.md) > Titanium Alloys

# Titanium Alloys

## Contents

- [Overview](#overview)
- [The oxygen prohibition](#the-oxygen-prohibition)
- [The alloys](#the-alloys)
- [ELI, and why it exists](#eli-and-why-it-exists)
- [The heat treatment trade](#the-heat-treatment-trade)
- [Stress corrosion in unexpected places](#stress-corrosion-in-unexpected-places)
- [Thermal conductivity](#thermal-conductivity)
- [Contamination and alpha case](#contamination-and-alpha-case)
- [Design rules of thumb](#design-rules-of-thumb)
- [Failure modes](#failure-modes)
- [Standards](#standards)
- [Tool interface](#tool-interface)
- [References](#references)

---

## Overview

Titanium has the best strength to weight available in a metal, and the reason it is not used everywhere is a list of prohibitions and a thermal conductivity fifteen times worse than aluminium.

For a fuel-side pressure vessel it is close to unbeatable. For anything touching an oxidiser it is disqualified, and the disqualification is absolute.

---

## The oxygen prohibition

**Titanium is impact sensitive in oxygen. It ignites and it burns.**

| Prohibited in | Why |
|---|---|
| **LOX, GOX** | Impact ignition. A particle strike or a pressure surge is enough |
| **N2O4, MON-1** | Stress corrosion cracking at 12 MPa in the uninhibited grades |
| **IRFNA, RFNA** | Same mechanism, faster |
| **Methanol** | SCC at 8 MPa. A common shop solvent |
| Dry chlorine | Ignition |
| Cadmium, mercury | Solid metal embrittlement |

**This is not a caution to weigh against mass.** The [`MaterialDatabase`](../aerospaceMaterialsLibrary/MaterialDatabase.py) class raises a `CompatibilityError` rather than returning a warning, and the [`MaterialSelector`](../aerospaceMaterialsLibrary/MaterialSelector.py) rejects the alloy outright rather than ranking it low.

**The MON-1 history is worth knowing.** Nitrogen tetroxide was found to crack titanium tankage in the 1960s, and the fix was to add a small nitric oxide content, producing MON-1. The uninhibited grade is still prohibited and the inhibited grade is a controlled specification, not a nominal composition.

**The methanol threshold is the one that catches people in the shop.** Eight MPa is a residual stress, not a design stress, and methanol is an ordinary cleaning solvent. Titanium hardware has been cracked by a cleaning operation.

---

## The alloys

| Alloy | Fty [MPa] | Ftu [MPa] | K_Ic | Where it belongs |
|---|---|---|---|---|
| **Ti-6Al-4V annealed** | 880 | 950 | 75 | The default. Pressure vessels, fittings |
| Ti-6Al-4V STA | 1035 | 1103 | 49 | Higher strength, much lower toughness |
| **Ti-6Al-4V ELI** | 795 | 860 | **100** | Cryogenic and fracture critical |
| CP Ti grade 2 | 275 | 345 | 110 | Corrosion service, weldable, formable |
| **Ti-3Al-2.5V** | 586 | 621 | 70 | **Tubing, and essentially the only choice** |

**Ti-3Al-2.5V is the titanium tubing alloy.** It is formable enough to be drawn and bent cold, which 6-4 is not, at 56 percent the density of a stainless line. Standard for aircraft hydraulic lines and used for spacecraft propellant lines where the mass saving justifies the cost and the fuel-side-only restriction.

---

## ELI, and why it exists

Extra low interstitial: oxygen held to 0.13 percent instead of 0.20.

| Property | Grade 5 | Grade 23 (ELI) | Change |
|---|---|---|---|
| Yield strength | 880 | 795 | -10 % |
| **Fracture toughness** | 75 | **100** | **+33 %** |
| Toughness ratio at 20 K | 0.72 | **0.84** | Far better cold |

**Oxygen is an interstitial strengthener and an embrittler at the same time.** Removing it costs strength and buys toughness, and for a fracture critical or cryogenic part that is the right direction.

The critical flaw size goes as toughness squared, so a 33 percent toughness gain is a 78 percent larger tolerable flaw at the same stress. That is usually worth far more than 10 percent of the yield strength.

**Grade 23 carries the identical oxygen prohibition.** ELI refers to the interstitial content of the alloy, not to its compatibility.

---

## The heat treatment trade

Solution treating and aging raises the strength and costs toughness, and on a fracture critical vessel that is usually the wrong trade.

| Condition | A-basis Fty | K_Ic | Critical flaw at 524 MPa |
|---|---|---|---|
| **Annealed** | 828 MPa | 75 MPa-sqrt(m) | **5.19 mm** |
| STA | 965 MPa | 49 MPa-sqrt(m) | 2.22 mm |

From the [worked example](../codeInterface.py): the bottle wall is 2.62 mm. The annealed condition has a critical flaw twice the wall, so it leaks before it bursts. **The STA condition has a critical flaw below the wall thickness, so it does not.**

**The stronger heat treatment makes the vessel less safe**, and nothing in a strength table shows that. It is visible only when the fracture calculation is done.

---

## Stress corrosion in unexpected places

| Environment | Threshold [MPa] |
|---|---|
| Salt fog | 55 |
| MON-1 | 40 |
| **Uninhibited N2O4** | **12** |
| **Methanol** | **8** |

**The low numbers are all solvents and oxidisers**, and they are all reached by residual stress alone. A titanium part with an unrelieved machining or forming residual stress, wiped with methanol, can crack on the bench.

**Hydrogen is a separate problem.** Titanium forms a brittle hydride, and the notched ratio of 0.75 understates the risk for sustained exposure. Titanium is used in liquid hydrogen tankage where it stays cold, and it is not a high pressure gaseous hydrogen material.

---

## Thermal conductivity

**6.7 W/m-K, which is fifteen times worse than aluminium and half that of stainless.**

| Alloy | Thermal conductivity [W/m-K] |
|---|---|
| GRCop-42 | 320 |
| 6061-T6 | 167 |
| 316L | 16.3 |
| Inconel 718 | 11.4 |
| **Ti-6Al-4V** | **6.7** |

This makes a titanium part in a thermal path a thermal problem. A titanium boss on a cryogenic tank is a good heat leak barrier and a bad heat sink, and a titanium bracket carrying a heat load will run hot.

It also makes titanium difficult to machine: the heat does not conduct away from the cutting edge, so tool life is short and the surface can be locally overheated and contaminated.

---

## Contamination and alpha case

**Titanium picks up oxygen and nitrogen readily above about 800 K**, forming a hard brittle surface layer called alpha case. It is a fatigue crack initiation site and it must be removed.

| Source | Control |
|---|---|
| Hot forming | Chem mill the alpha case off afterwards, typically 0.05 to 0.15 mm per surface |
| Welding | Full inert shielding of weld, HAZ and back side. Discolouration other than light straw is a reject |
| Heat treatment | Vacuum or inert atmosphere |
| Machining | Sharp tools, flood coolant, no dwell |

**The chem mill allowance comes off the wall thickness** and has to be added to the stock dimension. On a thin-walled part that is a real fraction of the section.

**Weld discolouration is a rejection criterion, not a cosmetic one.** Straw is acceptable, blue is marginal, grey or white powdery is a reject. The colour is an oxide thickness gauge and it correlates directly with the embrittlement.

---

## Design rules of thumb

| Rule | Value |
|---|---|
| Never in any oxidiser system | Absolute. LOX, GOX, N2O4, nitric acid |
| Never cleaned with methanol | SCC threshold 8 MPa |
| Annealed rather than STA for pressure vessels | Critical flaw goes as toughness squared |
| ELI for cryogenic and fracture critical | 33 % more toughness for 10 % of the yield |
| Ti-3Al-2.5V for tubing | The only formable titanium tube alloy |
| Full inert shielding when welding | Front, back and HAZ |
| Chem mill alpha case after hot forming | 0.05 to 0.15 mm per surface |
| Not a thermal path material | 6.7 W/m-K |
| Not a high pressure gaseous hydrogen material | Hydride formation |

---

## Failure modes

**Titanium in an oxidiser system.** Ignition and a burning propellant line.

**A titanium part cleaned with methanol.** Cracking at residual stress levels.

**STA specified for a pressure vessel.** Higher strength, no leak before burst.

**Alpha case left on after hot forming.** Fatigue cracks initiating at the brittle surface layer.

**A weld with grey or powdery discolouration accepted.** Irreversibly embrittled joint.

**A titanium bracket used as a heat sink.** It is not one.

**6-4 specified for tubing.** It cannot be cold drawn or bent; the alloy is Ti-3Al-2.5V.

---

## Standards

| Standard | Scope |
|---|---|
| **MMPDS Chapter 5** | Titanium alloy allowables |
| AMS 4911 | Ti-6Al-4V sheet, strip and plate |
| AMS 4928 | Ti-6Al-4V bar and forging |
| AMS 4930 / 4907 | Ti-6Al-4V ELI |
| **AMS 4944 / 4945** | Ti-3Al-2.5V tubing |
| ASTM B265 / B348 | Titanium plate and bar |
| ASTM F136 | Ti-6Al-4V ELI |
| **AMS 4999** | Additive manufactured Ti-6Al-4V |
| AMS 2801 | Heat treatment of titanium alloy parts |
| **ASTM G86** | Ignition sensitivity to mechanical impact in oxygen |
| NASA-STD-6001 | Flammability and compatibility, including LOX impact |

---

## Tool interface

```python
# the rejection below is the point of the example, so it is caught
try:
    from MaterialDatabase import MaterialDatabase
    from DamageTolerance import DamageTolerance

    # The prohibition, enforced rather than documented
    database = MaterialDatabase()
    database.setInputs({'material': 'Ti-6Al-4V', 'condition': 'annealed'})
    database.checkCompatibility('LOX')       # raises CompatibilityError

    # The heat treatment trade, quantified
    for condition in ('annealed', 'sta'):
        damage = DamageTolerance()
        damage.setInputs({'material': 'Ti-6Al-4V', 'condition': condition,
                          'operatingStress': 524.4e6, 'wallThickness': 0.00262})
        damage.calculateCriticalFlaw()
        print(condition, damage.criticalFlawSize * 1000.0, damage.checkLeakBeforeBurst()['leakBeforeBurst'])
except Exception as error:
    print('rejected as expected: {}'.format(type(error).__name__))
```

---

## References

1. MMPDS-18, Chapter 5, *Titanium*.
2. Boyer, R., Welsch, G. and Collings, E. W. (eds.), *Materials Properties Handbook: Titanium Alloys*, ASM, 1994.
3. Leyens, C. and Peters, M. (eds.), *Titanium and Titanium Alloys*, Wiley-VCH, 2003.
4. NASA-STD-6001B, *Flammability, Offgassing, and Compatibility Requirements and Test Procedures*.
5. Lutjering, G. and Williams, J. C., *Titanium*, 2nd ed., Springer, 2007.
