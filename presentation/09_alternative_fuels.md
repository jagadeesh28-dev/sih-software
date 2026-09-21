# Slide 9: Alternative Marine Fuel Evaluation & Thermodynamic Grounding

## Physical Grounding: Invariant Shaft-Work Equivalence
Comparing different marine fuels cannot be done by volume or raw mass because lower heating values (LHV) and brake thermal efficiencies vary widely.
The platform uses the **Invariant Shaft-Work Principle**:

$$E_{\text{shaft}} = P_B \cdot t = m_{\text{fuel}} \cdot \text{LHV}_{\text{fuel}} \cdot \eta_{\text{thermal}}$$

$$\implies m_{\text{fuel}} = \frac{E_{\text{shaft}}}{\text{LHV}_{\text{fuel}} \cdot \eta_{\text{thermal}}}$$

```
  Cruise Voyage Shaft Energy Demand: E_shaft = 56,835 MJ/h (from VLSFO baseline)
  ─────────────────────────────────────────────────────────────────────────────
  Fuel Carrier       LHV (MJ/kg)    Brake Efficiency    Required Mass Flow (kg/h)
  ─────────────────────────────────────────────────────────────────────────────
  VLSFO              42.7           48.0%               2,740.86 kg/h (Baseline)
  MGO                42.8           48.0%               2,734.46 kg/h
  Bio-Methanol       19.9           46.0%               6,136.84 kg/h (+123.9%)
  Green Ammonia      18.6           44.0%               6,864.21 kg/h (+150.4%)
  Liquid Hydrogen   120.0           50.0%                 936.28 kg/h (-65.8%)
```

---

## Strict Scientific Boundary: Telemetry vs Simulation

| Fuel | Telemetry Status | Emissions Origin | Regulatory Standard |
|:---|:---|:---|:---|
| **VLSFO** | **Real Measured Telemetry** (105k+ records) | Flow meters & shaft torquemeter | IMO MARPOL VI |
| **MGO** | **Real Measured Telemetry** (Aux & Main) | Flow meters & shaft torquemeter | IMO MARPOL VI |
| **Fossil LNG** | Thermodynamic Scenario Simulation | Dual-fuel Otto cycle conversion | FuelEU Maritime |
| **Bio-Methanol** | Thermodynamic Scenario Simulation | Compression-ignition dual-fuel | IMO MEPC.391(81) |
| **Green Ammonia** | Thermodynamic Scenario Simulation | Zero-carbon combustion model | IMO MEPC.391(81) |
| **Liquid Hydrogen** | Thermodynamic Scenario Simulation | PEM Fuel Cell / Cryo combustion | IMO Resolution MEPC |

---

## Safe Scientific Claim
Alternative-fuel metrics are **scenario estimates** under stated thermodynamic assumptions. We do not claim measured operational data for green ammonia or hydrogen where real telemetry does not exist.
