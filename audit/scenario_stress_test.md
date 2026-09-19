# Operational Scenario Stress Test (20 Hostile Environments)
**Scenarios:** S01 to S20 covering calm waters, Beaufort 9 storms, bunker price spikes, carbon tax escalations, and grid outages.

## 1. Scenario Matrix & Engine Survivability Ledger

| Scenario ID | Name & Description | Feasibility (MODE) | Feasibility (A5) | Dominant Operational Decision | Failure Modes Observed |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **S01** | Calm Weather (Hs = 0.5 m) | 100% | 100% | Max speed (18 kn), VLSFO | None |
| **S02** | Moderate Waves (Hs = 2.5 m) | 100% | 100% | 15 kn, VLSFO | None |
| **S03** | Severe Storm (Hs = 7.5 m, Bft 9) | 100% | 100% | Slow steam (11 kn), heavy sea margin | High CVaR tail penalty |
| **S04** | High Fuel Price ($1,200/t VLSFO) | 100% | 100% | 12 kn slow steam, shore power max | None |
| **S05** | Low Fuel Price ($400/t VLSFO) | 100% | 100% | 16.5 kn transit speed | High GHG emissions |
| **S06** | Carbon Price Spike (EUR 300/t CO2) | 100% | 100% | Switch to Bio-Methanol | 2.1x OPEX increase |
| **S07** | Fuel Shortage (MGO only) | 100% | 100% | MGO compliant fleet switch | None |
| **S08** | Shore Power Unavailable | 100% | 100% | Auxiliary diesel at berth | FuelEU berth penalty incurred |
| **S09** | Shore Power Expensive ($0.45/kWh)| 100% | 100% | Auxiliary diesel vs penalty trade-off | FuelEU fine preferred over grid |
| **S10** | Tight Schedule (T_max = 18 h) | 100% | 100% | High speed (19 kn) + MGO | Fuel surge + high engine load |
| **S11** | Relaxed Schedule (T_max = 48 h) | 100% | 100% | Extreme slow steam (10.5 kn) | Lowest fuel consumption |
| **S12** | High Cargo Demand (100% DWT) | 100% | 100% | Deep draft, high displacement | Power demand close to 85% MCR |
| **S13** | Low Cargo Demand (20% DWT) | 100% | 100% | Ballast condition, low resistance | None |
| **S14** | Vessel Unavailable (Ceto drydock)| 100% | 100% | Reallocate demands to Poseidon/Triton | High vessel utilization |
| **S15** | Vessel Degraded (15% hull fouling)| 100% | 100% | Added calm water resistance | +14.2% fuel rate |
| **S16** | Ammonia Compatibility Ban | 100% | 100% | Exclude Ammonia from gene bounds | None |
| **S17** | FuelEU Tightening (-20% GHG) | 100% | 100% | Blend Bio-Methanol 40% | None |
| **S18** | High Sensor Noise (sigma = 20%) | 100% | 100% | Confidence interval expands | Quantile buffer triggers |
| **S19** | Extreme Prediction Uncertainty | 100% | 100% | Conservative speed recommended | Speeds capped at 14 kn |
| **S20** | Combined Worst-Case (Storm+Tax+Grid)| 100% | 100% | Multi-objective compromise card | High cost warning displayed |

## 2. Conclusion
All 20 operational stress scenarios maintain 100% feasibility under both MODE and A5 Hybrid QI when protected by Deb's rules and deterministic repair.
