# Slide 6: Executable Operational Cost Minimization Model

## Complete Operational Cost Formulation
The fleet operational expenditure (OPEX) is computed transparently without double counting:

$$C_{\text{total}} = C_{\text{fuel}} + C_{\text{OPS}} + C_{\text{carbon}} + C_{\text{schedule}} + C_{\text{FuelEU}}$$

```
  ┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
  │   Bunker Cost   │  +  │ Shore Power (OPS)│  +  │  Carbon Pricing │
  │   C_fuel        │     │ C_OPS            │     │  C_carbon       │
  │ (mass * $/t)    │     │ (kWh * $/kWh+fee)│     │  (CO2 * $/t)    │
  └────────┬────────┘     └────────┬─────────┘     └────────┬────────┘
           │                       │                        │
           └───────────────────────┼────────────────────────┘
                                   │
                                   ▼
                       ┌────────────────────────┐
                       │ Total Operational Cost │
                       │ C_total ($/voyage)     │
                       └────────────────────────┘
                                   ▲
           ┌───────────────────────┴────────────────────────┐
           │                                                │
  ┌────────┴────────┐                              ┌────────┴────────┐
  │ Schedule Penalty│                              │ FuelEU Penalty  │
  │ C_schedule      │                              │ C_FuelEU        │
  │ (delay * $/h)   │                              │ (GHG deficit)   │
  └─────────────────┘                              └─────────────────┘
```

---

## Dynamic Configuration-Driven Price Registry
Prices are loaded dynamically from `configs/fuels.yaml` and `configs/regulations.yaml`:
- **VLSFO Baseline**: $620.00 / t
- **MGO Bunker**: $850.00 / t
- **Fossil LNG**: $750.00 / t
- **Bio-Methanol**: $1,050.00 / t
- **Port OPS Tariff**: $0.18 / kWh + $500 connection fee
- **EU ETS Carbon Price**: $90.00 / t $\text{CO}_2$ (biogenic emissions zero-rated)
- **Charter Demurrage Rate**: $2,500.00 / hour overdue

---

## Verified Sensitivity & Optimization Integration
- **Linear Elasticity**: Verified across unit tests in `tests/test_sih_requirements.py` ($\Delta C / \Delta P = m_{\text{fuel}}$).
- **Zero Double-Counting**: Explicitly separates propulsion energy, port hoteling electricity, and carbon instruments.
- **Optimization Impact**: Shifting from pure fuel focus to operational cost focus alters optimal dispatch speeds and port connection decisions.
