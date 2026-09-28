# PHASE 3 REGULATORY MODEL
**Project:** SIH26138 — Egreen Quanta: Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization  
**Stage:** Maritime Environmental Regulations Decoupling & Compliance Formulation  
**Date:** 2026-09-12  
**Status:** REGULATORY SPECIFICATION LOCKED  

---

## 1. Regulatory Decoupling Principle

A critical flaw identified in commercial and academic maritime tools is the conflation of distinct regulatory frameworks into a generic "green score." In SIH26138, four maritime decarbonization frameworks are mathematically decoupled and evaluated independently:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          MARITIME REGULATORY TAXONOMY                                  │
├───────────────────┬───────────────────┬────────────────────────┬───────────────────────┤
│    FRAMEWORK      │   METRIC BASIS    │      SCOPE UNITS       │       AUTHORITY       │
├───────────────────┼───────────────────┼────────────────────────┼───────────────────────┤
│ 1. IMO MEPC.391   │ Full Lifecycle    │ g CO2e / MJ            │ IMO Global            │
│    (81) LCA       │ (Well-to-Wake)    │ Energy-specific        │ Resolution MEPC.391   │
├───────────────────┼───────────────────┼────────────────────────┼───────────────────────┤
│ 2. IMO CII        │ Tank-to-Wake      │ g CO2 / (DWT * nm)     │ MARPOL Annex VI       │
│    (Operational)  │ Combustion CO2    │ Annual Transport Work  │ Regulation 28         │
├───────────────────┼───────────────────┼────────────────────────┼───────────────────────┤
│ 3. FuelEU         │ Well-to-Wake      │ g CO2e / MJ            │ European Union        │
│    Maritime       │ GHG Intensity     │ Statutory Deficit EUR  │ Regulation 2023/1805  │
├───────────────────┼───────────────────┼────────────────────────┼───────────────────────┤
│ 4. EU ETS         │ Tank-to-Wake      │ Metric Tonnes CO2      │ European Union        │
│    Maritime       │ Direct CO2 (CH4)  │ Statutory Allowances   │ Directive 2023/959    │
└───────────────────┴───────────────────┴────────────────────────┴───────────────────────┘
```

---

## 2. Framework A: IMO Lifecycle GHG Intensity (MEPC.391(81))

### 2.1 Applicability & Scope
- **Applicability**: Global maritime shipping; foundational emission factors for alternative fuel evaluation.
- **Scope**: Complete Well-to-Wake (WtW) lifecycle accounting, including upstream extraction, synthesis, refining, liquefaction, bunkering, and onboard combustion/slip.

### 2.2 Mathematical Formulation
$$\text{GHG}_{\text{WtW, total}} = \sum_{i} \left( \text{GHG}_{\text{WtT}, i} + \text{GHG}_{\text{TtW}, i} \right) \quad [\text{tonnes CO}_2\text{e}]$$

1. **Well-to-Tank (Upstream Extraction/Production)**:
   $$\text{GHG}_{\text{WtT}, i} = \frac{m_{f, i} \cdot \text{LHV}_i \cdot e_{\text{WtT}, i}}{10^6}$$
   where $m_{f, i}$ is fuel mass ($\text{kg}$), $\text{LHV}_i$ is Lower Heating Value ($\text{MJ/kg}$), and $e_{\text{WtT}, i}$ is upstream intensity factor ($\text{g CO}_2\text{e/MJ}$).

2. **Tank-to-Wake (Onboard Combustion & Fugitive Slip)**:
   $$\text{GHG}_{\text{TtW}, i} = \frac{m_{f, i} \cdot C_{f, i}}{1000} + \frac{m_{f, i} \cdot e_{\text{N}_2\text{O}, i} \cdot \text{GWP}_{\text{N}_2\text{O}}}{10^6} + \frac{m_{f, i} \cdot \sigma_{\text{slip}, i} \cdot \text{GWP}_{\text{CH}_4}}{1000}$$
   where:
   - $C_{f, i}$: Carbon conversion factor ($\text{g CO}_2\text{/g fuel}$)
   - $\text{GWP}_{100, \text{CH}_4} = 29.8$ (IPCC AR6 100-year basis)
   - $\text{GWP}_{100, \text{N}_2\text{O}} = 273.0$ (IPCC AR6 100-year basis)
   - $\sigma_{\text{slip}, i}$: Engine-specific methane slip fraction (e.g. $0.022$ for LNG 4-stroke LPDF).

---

## 3. Framework B: IMO Carbon Intensity Indicator (CII)

### 3.1 Applicability & Boundary Conditions
- **Applicability**: Cargo, container, bulk, and cruise vessels $\ge 5,000\text{ GT}$ trading internationally under MARPOL Annex VI.
- **Reference Resolution**: IMO Resolution MEPC.338(76), MEPC.354(78).
- **Time Horizon**: Annual operational metric; voyage calculations provide operational trajectory estimates.

### 3.2 Mathematical Formulation
1. **Attained CII**:
   $$\text{CII}_{\text{attained}} = \frac{\sum_i m_{f, i} \cdot C_{f, i} \cdot 10^3}{\text{Capacity} \cdot \text{Distance}} \quad \left[ \frac{\text{g CO}_2}{\text{DWT} \cdot \text{nm}} \text{ or } \frac{\text{g CO}_2}{\text{GT} \cdot \text{nm}} \right]$$
   where $\text{Capacity}$ is $\text{DWT}$ for cargo vessels and $\text{GT}$ for cruise passenger ships.

2. **CII Reference Line**:
   $$\text{CII}_{\text{ref}} = a \cdot \text{Capacity}^{-c}$$
   Parameters (IMO MEPC.338(76)):
   - *Cruise Passenger Ships ($\ge 100,000\text{ GT}$)*: $a = 930, c = 0.381$
   - *Container Ships*: $a = 1984, c = 0.489$
   - *Bulk Carriers*: $a = 4745, c = 0.622$
   - *Offshore Supply Vessels*: Not mandatory under current Annex VI Reg 28 (`NOT_APPLICABLE`).

3. **Required CII (Target)**:
   $$\text{CII}_{\text{required}} = \text{CII}_{\text{ref}} \cdot \left( 1 - \frac{Z}{100} \right)$$
   where annual reduction factor $Z = 11\%$ for year 2026 ($2.0\%$ annual escalation).

4. **Operational Rating Boundaries**:
   Let ratio $R = \text{CII}_{\text{attained}} / \text{CII}_{\text{required}}$:
   $$\text{Rating} = \begin{cases}
   \mathbf{A} & \text{if } R \le 0.83 \quad (\text{Superior}) \\
   \mathbf{B} & \text{if } 0.83 < R \le 0.94 \quad (\text{Minor Superior}) \\
   \mathbf{C} & \text{if } 0.94 < R \le 1.06 \quad (\text{Moderate / Compliant}) \\
   \mathbf{D} & \text{if } 1.06 < R \le 1.19 \quad (\text{Inferior - Corrective Action Plan required after 3 yrs}) \\
   \mathbf{E} & \text{if } R > 1.19 \quad (\text{Unacceptable - Immediate Corrective Plan required})
   \end{cases}$$

---

## 4. Framework C: FuelEU Maritime (Regulation (EU) 2023/1805)

### 4.1 Applicability & Scope
- **Applicability**: Commercial ships $\ge 5,000\text{ GT}$ calling at European Economic Area (EEA) ports.
- **Scope**:
  - $100\%$ of energy consumed between two EEA ports.
  - $100\%$ of energy consumed at berth in EEA ports.
  - $50\%$ of energy consumed on voyages between an EEA port and a non-EEA port.

### 4.2 GHG Intensity Target Trajectory
Baseline (2020 reference): $91.16\text{ g CO}_2\text{e/MJ}$.
- **2025–2029**: $-2\%$ reduction $\to \mathbf{89.3368\text{ g CO}_2\text{e/MJ}}$
- **2030–2034**: $-6\%$ reduction $\to 85.6904\text{ g CO}_2\text{e/MJ}$
- **2035–2039**: $-14.5\%$ reduction $\to 77.9418\text{ g CO}_2\text{e/MJ}$
- **2040–2044**: $-31\%$ reduction $\to 62.9004\text{ g CO}_2\text{e/MJ}$
- **2045–2049**: $-62\%$ reduction $\to 34.6408\text{ g CO}_2\text{e/MJ}$
- **2050 onwards**: $-80\%$ reduction $\to 18.2320\text{ g CO}_2\text{e/MJ}$

### 4.3 Compliance Balance & Statutory Penalty
1. **Attained GHG Intensity**:
   $$\text{GHGIE}_{\text{actual}} = \frac{\sum_i \text{GHG}_{\text{WtW}, i} \cdot 10^6}{\sum_i m_{f, i} \cdot \text{LHV}_i} \quad \left[ \frac{\text{g CO}_2\text{e}}{\text{MJ}} \right]$$

2. **Compliance Balance (CB)**:
   $$\text{CB} = \left( \text{Target} - \text{GHGIE}_{\text{actual}} \right) \times \sum_i \left( m_{f, i} \cdot \text{LHV}_i \right) \quad [\text{g CO}_2\text{e}]$$
   - If $\text{CB} \ge 0$: **Compliance Surplus** (bankable or poolable under Articles 20/21).
   - If $\text{CB} < 0$: **Compliance Deficit** (triggers statutory penalty).

3. **Statutory Financial Penalty**:
   $$\text{Penalty}_{\text{FuelEU}} = \left( \frac{|\text{CB}|}{\text{Target} \times 41,000\text{ MJ/t}} \right) \times 2,400\text{ EUR/t VLSFO equivalent}$$

---

## 5. Framework D: EU Emissions Trading System (Directive 2023/959)

### 5.1 Applicability & Phase-In Schedule
- **Applicability**: $\ge 5,000\text{ GT}$ ships calling at EEA ports.
- **Coverage**: $100\%$ intra-EEA voyages and port calls, $50\%$ extra-EEA voyages.
- **Phase-In Schedule**:
  - 2024: $40\%$ of verified $\text{CO}_2$ emissions.
  - 2025: $70\%$ of verified $\text{CO}_2$ emissions.
  - **2026 onwards**: $\mathbf{100\%}$ of verified $\text{CO}_2$, $\text{CH}_4$, and $\text{N}_2\text{O}$ emissions.

### 5.2 Financial Allowance Liability
$$\text{Cost}_{\text{ETS}} = \text{Scope}_{\text{EEA}} \cdot \text{Surrender\_Pct} \cdot \text{GHG}_{\text{TtW}} \cdot P_{\text{EUA}}$$
where $P_{\text{EUA}}$ is the European Union Allowance price (default: $90.0\text{ EUR/tonne CO}_2\text{e}$, configurable).

---

## 6. Regulatory Output Data Contract

Every optimization candidate evaluation outputs a structured `RegulatoryStatus` object:

```json
{
  "imo_lifecycle": {
    "wtw_total_tonnes_co2e": 142.50,
    "wtt_tonnes_co2e": 24.10,
    "ttw_tonnes_co2": 115.20,
    "methane_slip_tonnes_co2e": 3.20
  },
  "imo_cii": {
    "attained_cii": 12.45,
    "required_cii": 14.10,
    "ratio": 0.883,
    "rating": "B",
    "status": "COMPLIANT"
  },
  "fueleu_maritime": {
    "attained_intensity_g_mj": 88.10,
    "target_intensity_g_mj": 89.34,
    "compliance_balance_g": 24800000.0,
    "penalty_eur": 0.0,
    "status": "COMPLIANT"
  },
  "eu_ets": {
    "taxable_tonnes_co2e": 118.40,
    "allowance_cost_usd": 11508.48,
    "status": "SURRENDER_REQUIRED"
  },
  "overall_regulatory_verdict": "COMPLIANT"
}
```

If a required input (e.g. ship capacity or voyage distance) is absent, the system strictly returns `INSUFFICIENT_DATA` or `NOT_APPLICABLE` and never invents arbitrary compliant values.
