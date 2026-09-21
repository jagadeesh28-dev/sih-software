# Slide 7: Lifecycle Well-to-Wake GHG Minimization Model

## Complete Lifecycle GHG Accounting (IMO MEPC.391(81))
Decarbonization compliance cannot rely on tailpipe emissions alone. The system implements full Well-to-Wake (WtW) lifecycle accounting:

$$\text{GHG}_{\text{WtW}} = \text{GHG}_{\text{WtT}} + \text{GHG}_{\text{TtW}} + \text{GHG}_{\text{fugitive}}$$

```
  ┌─────────────────────────┐          ┌─────────────────────────┐
  │   Well-to-Tank (WtT)    │    +     │   Tank-to-Wake (TtW)    │
  │   Upstream Production   │          │   Combustion Emissions  │
  │   Extraction & Refining │          │   CO2 + 298*N2O + 28*CH4│
  └────────────┬────────────┘          └────────────┬────────────┘
               │                                    │
               └──────────────────┬─────────────────┘
                                  │
                                  ▼
                     ┌───────────────────────────┐
                     │ Well-to-Wake GHG Total    │
                     │ (tonnes CO2-equivalent)   │
                     └───────────────────────────┘
                                  ▲
                                  │
                     ┌────────────┴──────────────┐
                     │   Fugitive Emissions      │
                     │   Unburnt Methane Slip    │
                     │   (Low-Pressure Dual-Fuel)│
                     └───────────────────────────┘
```

---

## 6-Pathway Lifecycle Parameter Registry

| Marine Fuel Pathway | LHV (MJ/kg) | Upstream WtT ($\text{gCO}_2\text{e/MJ}$) | Combustion TtW ($\text{tCO}_2\text{/t}$) | Total WtW ($\text{gCO}_2\text{e/MJ}$) | Data Origin |
|:---|---:|---:|---:|---:|:---|
| **VLSFO (0.5% S)** | 42.7 | 13.5 | 3.114 | 91.10 | **Measured Telemetry** |
| **MGO (0.1% S)** | 42.8 | 14.4 | 3.206 | 93.30 | **Measured Telemetry** |
| **Fossil LNG** | 49.1 | 18.5 | 2.750 | 88.20 | Scenario Simulation |
| **Bio-Methanol** | 19.9 | 15.0 | 0.000* | 28.50 | Scenario Simulation |
| **Green Ammonia** | 18.6 | 8.0 | 0.000 | 8.00 | Scenario Simulation |
| **Liquid Hydrogen** | 120.0 | 5.0 | 0.000 | 5.00 | Scenario Simulation |

*\*Biogenic combustion $\text{CO}_2$ is zero-rated under EU ETS/IMO LCA guidelines; upstream footprint tracks cultivation and processing.*

---

## Scenario Verification (CPS_Poseidon 250 nm Voyage)
- **VLSFO Conventional**: 44.64 t fuel $\to$ 141.28 t combustion $\to$ **165.51 t WtW $\text{CO}_2\text{e}$**
- **Bio-Methanol**: 90.18 t fuel $\to$ 125.23 t gross $\to$ **153.95 t WtW $\text{CO}_2\text{e}$** (-7.0%)
- **Green Ammonia**: 96.49 t fuel $\to$ 13.17 t pilot $\to$ **29.33 t WtW $\text{CO}_2\text{e}$** (**-82.3%**)
- **Liquid Hydrogen**: 14.96 t fuel $\to$ 0.00 t combustion $\to$ **23.34 t WtW $\text{CO}_2\text{e}$** (**-85.9%**)
