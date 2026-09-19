# Alternative Marine Fuel Lifecycle (LCA) Audit
**Fuel Pathway Database:** FuelPathwayRegistry calibrated to Fourth IMO GHG Study & RED II standards.

## 1. Certified Fuel Parameter Matrix

| Fuel Key | Description | LHV (MJ/kg) | WtT Factor (g/MJ) | TtW Factor (g/MJ) | WtW Total (g/MJ) | Methane Slip (%) | Unit Cost ($/t) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **vlsfo** | Very Low Sulphur Fuel Oil | 41.0 | 13.50 | 77.00 | **90.50** | 0.0% | $620 |
| **mgo** | Marine Gas Oil | 42.7 | 14.20 | 74.50 | **88.70** | 0.0% | $850 |
| **fossil_lng** | Liquefied Natural Gas | 48.0 | 18.50 | 56.50 + Slip | **92.20** | **2.2%** | $780 |
| **bio_methanol** | Biomass-Derived Methanol | 19.9 | 15.00 | 0.00 (Biogenic) | **15.00** | 0.0% | $1,150 |
| **green_ammonia**| Renewable e-Ammonia | 18.6 | 8.50 | 0.00 | **8.50** | 0.0% | $1,450 |

## 2. Scientific Rules Enforced
1. **Zero-Emission Myth Falsified:** No fuel is called "zero emission." Even Green Ammonia incurs 8.50 gCO2e/MJ during Well-to-Tank synthesis and transport.
2. **Methane Slip Reality:** Fossil LNG burns cleaner at the funnel, but a 2.2% methane slip (GWP_100 = 29.8) makes its total WtW intensity (92.20 g/MJ) *higher* than VLSFO (90.50 g/MJ).
3. **Volumetric Density:** Methanol (19.9 MJ/kg) and Ammonia (18.6 MJ/kg) require more than double the fuel bunker mass to deliver equivalent energy as VLSFO (41.0 MJ/kg).
