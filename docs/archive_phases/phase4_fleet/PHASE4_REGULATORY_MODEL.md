# PHASE 4 REGULATORY MODEL
**Project:** SIH26138 — Egreen Quanta: Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization  
**Stage:** Heterogeneous Fleet Maritime Regulatory Architecture & Decoupled Compliance Formulation  
**Date:** 2026-09-14  
**Status:** COMPLETE & AUDITED  

---

## 1. Executive Summary & Regulatory Decoupling Principle

A recurring flaw identified in maritime optimization literature and commercial routing tools is the conflation of distinct statutory frameworks into an arbitrary, ungrounded "green score." In Phase 4, we rigorously decouple international (IMO) and regional (EU) statutory instruments across our heterogeneous fleet.

Every candidate solution evaluated in SIH26138 is subjected to separate, unbundled accounting under four distinct regulatory frameworks:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 4 DECOUPLED REGULATORY ARCHITECTURE                            │
├──────────────────────┬──────────────────────┬───────────────────────┬────────────────────────┤
│      FRAMEWORK       │     METRIC BASIS     │      SCOPE UNITS      │       STATUTORY        │
│                      │                      │                       │       AUTHORITY        │
├──────────────────────┼──────────────────────┼───────────────────────┼────────────────────────┤
│ 1. IMO MEPC.391(81)  │ Full Lifecycle       │ g CO2e / MJ           │ IMO Global Res.        │
│    LCA Framework     │ (Well-to-Wake)       │ Energy-specific       │ MEPC.391(81)           │
├──────────────────────┼──────────────────────┼───────────────────────┼────────────────────────┤
│ 2. IMO CII           │ Operational          │ g CO2 / (GT · nm)     │ MARPOL Annex VI        │
│    (Annual Rating)   │ (Tank-to-Wake CO2)   │ or g CO2 / (DWT · nm) │ Regulation 28          │
├──────────────────────┼──────────────────────┼───────────────────────┼────────────────────────┤
│ 3. FuelEU Maritime   │ Well-to-Wake         │ g CO2e / MJ           │ Regulation (EU)        │
│    (Intensity + OPS) │ Fleet Energy Pool    │ Statutory Deficit EUR │ 2023/1805              │
├──────────────────────┼──────────────────────┼───────────────────────┼────────────────────────┤
│ 4. EU ETS Maritime   │ Direct Emissions     │ Metric Tonnes CO2     │ Directive (EU)         │
│    (Carbon Price)    │ (Tank-to-Wake Scope) │ EUA Allowances USD    │ 2023/959               │
└──────────────────────┴──────────────────────┴───────────────────────┴────────────────────────┘
```

> [!CRITICAL]
> **DISCLAIMER OF STATUTORY COMPLIANCE**  
> Computational optimization within SIH26138 models statutory regulatory formulations as mathematical objective penalties and constraints. **Single-voyage or short-horizon optimization results DO NOT constitute legal regulatory certification, statutory classification, or official IMO/EU compliance approval.** Real-world annual CII compliance requires verified Data Collection System (DCS) data aggregated across a full calendar year.

---

## 2. Heterogeneous Fleet Regulatory Applicability Matrix

Because the Phase 4 fleet is heterogeneous across vessel types and service profiles, regulatory requirements differ fundamentally between vessels:

| Vessel Identifier | Statutory Type | Gross Tonnage (GT) | Deadweight (DWT) | IMO CII Scope | FuelEU Maritime Scope | Shore Power (OPS) Mandate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`CPS_Poseidon`** | Cruise Passenger Ship | 70,000 GT | 8,500 DWT | **Mandatory** ($GT$ basis) | **Mandatory** (EEA calls) | **Mandatory at Berth** (2030+) |
| **`CPS_Triton`** | Cruise Passenger Ship | 11,000 GT | 1,800 DWT | **Mandatory** ($GT$ basis) | **Mandatory** (EEA calls) | Recommended / Elective |
| **`OSS_Ceto`** | Offshore Supply Vessel | 24,000 GT | 12,000 DWT | **Exempt** (Annex VI R28) | **Voluntary / Pre-2027** | Elective |

---

## 3. Mathematical Formulations

### 3.1 Framework A: IMO Lifecycle WtW GHG Accounting (MEPC.391(81))

Lifecycle emissions are computed on a Well-to-Wake (WtW) basis by aggregating Well-to-Tank (upstream extraction, processing, bunkering) and Tank-to-Wake (combustion and fugitive slip) emissions:

$$\text{GHG}_{\text{WtW}, i} = \sum_{v \in \mathcal{V}} \left[ \frac{m_{f, v} \cdot \text{LHV}_{f, v} \cdot e_{\text{WtT}, f, v}}{10^6} + \frac{m_{f, v} \cdot C_{f, v}}{10^3} + \frac{m_{f, v} \cdot \sigma_{\text{slip}, f, v} \cdot \text{GWP}_{\text{CH}_4}}{10^3} \right] \quad [\text{t CO}_2\text{e}]$$

Where:
- $m_{f, v}$: Fuel mass consumed by vessel $v$ ($\text{kg}$)
- $\text{LHV}_{f, v}$: Lower heating value of chosen fuel ($\text{MJ/kg}$)
- $e_{\text{WtT}, f, v}$: Upstream emission factor ($\text{g CO}_2\text{e/MJ}$)
- $C_{f, v}$: Carbon combustion conversion factor ($\text{g CO}_2\text{/g fuel}$)
- $\sigma_{\text{slip}}$: Methane/fugitive slip fraction (e.g., $0.022$ for LNG dual-fuel Otto engines)
- $\text{GWP}_{\text{CH}_4} = 29.8$ (IPCC AR6 100-year metric)

---

### 3.2 Framework B: IMO Operational Carbon Intensity Indicator (CII)

For vessels subject to MARPOL Annex VI Regulation 28:
1. **Attained CII Proxy**:
   $$\text{CII}_{\text{attained}, v} = \frac{m_{f, v} \cdot C_{f, v} \cdot 10^3}{\text{Capacity}_v \cdot D_v} \quad \left[ \frac{\text{g CO}_2}{\text{GT} \cdot \text{nm}} \right]$$
   where $\text{Capacity}_v = \text{GT}_v$ for passenger ships and $D_v$ is distance travelled in nautical miles.

2. **Required CII Benchmark**:
   $$\text{CII}_{\text{ref}, v} = a \cdot \text{Capacity}_v^{-c}$$
   For cruise passenger ships ($GT \ge 100,000$ or smaller proxy): $a = 930$, $c = 0.381$.
   $$\text{CII}_{\text{req}, v} = \text{CII}_{\text{ref}, v} \cdot \left(1 - \frac{Z_{2026}}{100}\right)$$
   where $Z_{2026} = 11.0\%$ reduction from 2019 baseline.

3. **Operational Rating Boundary & Penalties**:
   Let ratio $R_v = \text{CII}_{\text{attained}, v} / \text{CII}_{\text{req}, v}$.
   - $R_v \le 0.83 \implies \text{Rating } \mathbf{A}$
   - $0.83 < R_v \le 0.94 \implies \text{Rating } \mathbf{B}$
   - $0.94 < R_v \le 1.06 \implies \text{Rating } \mathbf{C}$ (Standard Compliant)
   - $1.06 < R_v \le 1.19 \implies \text{Rating } \mathbf{D}$ (Corrective Action required)
   - $R_v > 1.19 \implies \text{Rating } \mathbf{E}$ (Inferior / Immediate plan required)

   **Penalty Formulation**:
   $$P_{\text{CII}, v} = \begin{cases} 0 & \text{if } R_v \le 1.06 \\ 10,000 \cdot (R_v - 1.06) & \text{if } R_v > 1.06 \end{cases}$$

---

### 3.3 Framework C: FuelEU Maritime (Regulation (EU) 2023/1805)

1. **GHG Intensity Requirement**:
   Statutory target for 2025–2029:
   $$\text{GHGIE}_{\text{target}} = 89.336 \quad [\text{g CO}_2\text{e/MJ}] \quad (2.0\% \text{ reduction from } 91.16 \text{ g CO}_2\text{e/MJ})$$

2. **Attained GHG Intensity**:
   $$\text{GHGIE}_{\text{actual}, v} = \frac{\text{GHG}_{\text{WtW}, v} \cdot 10^6}{\sum_{k} m_{k, v} \cdot \text{LHV}_{k, v}} \quad [\text{g CO}_2\text{e/MJ}]$$

3. **Statutory Compliance Balance & Financial Deficit**:
   $$\text{CB}_v = \left( \text{GHGIE}_{\text{target}} - \text{GHGIE}_{\text{actual}, v} \right) \times \sum_{k} \left( m_{k, v} \cdot \text{LHV}_{k, v} \right) \quad [\text{g CO}_2\text{e}]$$
   If $\text{CB}_v < 0$ (Deficit):
   $$\text{Penalty}_{\text{FuelEU}, v} = \frac{|\text{CB}_v|}{\text{GHGIE}_{\text{actual}, v} \times 41.0} \times 2400 \quad [\text{EUR}]$$
   Converted to USD using standard statutory exchange rate ($1.08 \text{ USD/EUR}$).

4. **Onshore Power Supply (OPS / Cold-Ironing) Mandate**:
   For cruise passenger ships calling at major EEA ports, shore power is mandatory during berth:
   $$\text{Penalty}_{\text{OPS}, v} = \begin{cases} 0 & \text{if } u_{\text{shore}, v} = 1 \\ 1.50 \text{ EUR/kWh} \times P_{\text{hotel}, v} \times t_{\text{berth}, v} & \text{if } u_{\text{shore}, v} = 0 \text{ and mandated} \end{cases}$$

---

### 3.4 Framework D: EU ETS Maritime (Directive (EU) 2023/959)

Direct combustion emissions (Tank-to-Wake $\text{CO}_2$, $\text{CH}_4$, $\text{N}_2\text{O}$) are subject to emissions surrender:
$$C_{\text{ETS}} = \text{Scope}_{\text{EEA}} \cdot \text{SurrenderPct}_{2026} \cdot \text{GHG}_{\text{TtW}} \cdot P_{\text{carbon}}$$
Where:
- $\text{Scope}_{\text{EEA}} = 1.0$ (intra-EEA benchmark voyages)
- $\text{SurrenderPct}_{2026} = 70\%$ phase-in for reporting year 2025/2026
- $P_{\text{carbon}} = 90.00 \text{ USD/tonne CO}_2$ baseline (sensitivity tested from $50$ to $250 \text{ USD/t}$)

---

## 4. Constraint Classification: Hard vs Modeled Soft

To prevent optimizer exploitation while maintaining realistic economic incentives, constraints are strictly categorized:

| Category | Constraints | Handling Mechanism | Penalty Value |
| :--- | :--- | :--- | :--- |
| **Hard Physical Barrier** | Safe Operating Envelope (speed, draft, power) | Immediate Rejection | $\ge 100,000$ |
| **Hard Combinatorial** | Demand collision, cargo capacity overload, fuel incompatibility | Combinatorial Safe Rejection | $\ge 50,000$ |
| **Modeled Regulatory** | FuelEU compliance deficit, EU ETS carbon surrender | Direct Financial Cost ($J_C$) | Statutory exact ($€2,400$/t deficit, $€90$/t EUA) |
| **Soft Operational** | IMO CII Rating D/E excursion, arrival deadline tardiness | Progressive Smooth Penalty | Proportional quadratic demurrage / penalty |

This decoupling ensures that the optimizer cannot game the system by trading a slight regulatory fine for an unphysical speed or unsafe draft.
