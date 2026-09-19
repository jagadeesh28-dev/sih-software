# PHASE 3 SCIENTIFIC ASSUMPTIONS & EVIDENCE LEDGER
**Project:** SIH26138 — Egreen Quanta: Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization  
**Stage:** Explicit Assumptions Inventory & Confidence Classification  
**Date:** 2026-09-12  
**Status:** ASSUMPTIONS INVENTORY LOCKED  

---

## 1. Taxonomy of Scientific Assumptions

To ensure complete transparency, every assumption in Phase 3 is cataloged and assigned an epistemological confidence rating:
- **`VALIDATED`**: Supported by verified physical measurements or empirical telemetry in this repository.
- **`EMPIRICALLY GROUNDED`**: Calibrated against established naval architecture literature and verified experimental datasets.
- **`HEURISTIC / ASSUMED`**: Engineering assumption required for tractability; explicitly flagged as non-ground-truth.
- **`DANGEROUS IF EXTRAPOLATED`**: Valid under strict local conditions, but produces severe errors or unphysical behavior if generalized.

---

## 2. Comprehensive Assumptions Inventory

### 2.1 Hydrodynamics & Predictive Physics

| ID | Assumption Statement | Confidence Status | Empirical Basis / Provenance | Danger / Boundary Condition |
| :--- | :--- | :---: | :--- | :--- |
| **A-PHYS-01** | *Instantaneous Fuel Mass Flow $\dot{m}_f(t)$ is predictable from operational and metocean kinematics without engine room telemetry.* | **`VALIDATED`** | FuelCast `CONFIG-REAL-A` achieves $R^2 = 0.9400$, $\text{MAE} = 263.91\text{ kg/h}$ across 173k real records. | Valid only within the empirical speed-draft envelope of the evaluated ships. |
| **A-PHYS-02** | *Holtrop-Mennen calm-water resistance provides a physically sound baseline prior.* | **`VALIDATED`** | Hybrid model (`MODEL-REAL-04`) achieves fleet-best $R^2 = 0.9501$, reducing MAE to $246.97\text{ kg/h}$ ($p = 7.45 \times 10^{-18}$). | Pure physics alone underpredicts by $-1,883\text{ kg/h}$ due to unmodeled auxiliary loads. |
| **A-PHYS-03** | *Involuntary speed loss in waves follows Kwon's empirical directional formulation.* | **`EMPIRICALLY GROUNDED`** | Kwon (1982) / Townsin & Kwon (1993); standardized in ITTC 7.5-02-07-02.2. | Overestimates speed loss if wave period is outside $4 - 15\text{ s}$ range. |
| **A-PHYS-04** | *Fuel consumption approaches a non-zero baseline at near-zero transit speed on cruise vessels.* | **`VALIDATED`** | FuelCast `CPS_Poseidon` exhibits $1,200 - 2,800\text{ kg/h}$ fuel burn at berth and maneuvering. | **DANGEROUS IF EXTRAPOLATED**: Assuming zero fuel at zero speed invalidates cruise voyage accounting. |
| **A-PHYS-05** | *A single hydrodynamic model can predict both cruise ships and offshore DP vessels.* | **`FALSIFIED`** | Leave-Vessel-Out $R^2 < 0$ across all 3 folds in Phase 2.3. | **STRICTLY PROHIBITED**: Must use vessel-class isolated models. |

### 2.2 Propulsion & Alternative Fuels

| ID | Assumption Statement | Confidence Status | Empirical Basis / Provenance | Danger / Boundary Condition |
| :--- | :--- | :---: | :--- | :--- |
| **A-FUEL-01** | *Alternative fuel mass requirements scale inversely with Lower Heating Value (LHV).* | **`EMPIRICALLY GROUNDED`** | First-principles chemical thermodynamics: $m_i = m_{\text{VLSFO}} \cdot (\text{LHV}_{\text{VLSFO}} / \text{LHV}_i) \cdot (\eta_{\text{VLSFO}} / \eta_i)$. | Assumes constant thermal efficiency $\eta$; ignores fuel-injection pump pressure limits. |
| **A-FUEL-02** | *Dual-fuel LNG engines exhibit a 2.2% unburned methane slip rate.* | **`EMPIRICALLY GROUNDED`** | ICCT (2024) maritime methane study; IMO MEPC.391(81) default for 4-stroke LPDF Otto engines. | High-pressure dual-fuel (HP-DF) Diesel cycle slips $< 0.2\%$; slip depends strongly on engine load. |
| **A-FUEL-03** | *Bio-methanol, ammonia, and hydrogen storage tanks require cargo volume penalties.* | **`EMPIRICALLY GROUNDED`** | DNV Maritime Forecast to 2050 (tank volume multipliers: 1.8x for LNG, 2.3x for MeOH, 2.7x for NH3, 4.8x for LH2). | Retrofitting older hulls may require deck placement rather than below-deck hold volume loss. |
| **A-FUEL-04** | *All alternative fuels are universally available at destination bunkering hubs.* | **`HEURISTIC / ASSUMED`** | Configurable scenario toggle in `configs/fuels.yaml`. | Green ammonia and LH2 bunkering infrastructure is currently nonexistent at most commercial ports. |

### 2.3 Economics & Operational Cost

| ID | Assumption Statement | Confidence Status | Empirical Basis / Provenance | Danger / Boundary Condition |
| :--- | :--- | :---: | :--- | :--- |
| **A-COST-01** | *VLSFO bunker price is reference $620/tonne; Bio-methanol $950/t; Ammonia $1100/t.* | **`EMPIRICALLY GROUNDED`** | Clarksons Shipping Intelligence Network & Methanol Institute (2024 quarterly average). | Bunker spot prices exhibit extreme volatility ($400 - 1100\text{ USD/t}$). Requires sensitivity analysis. |
| **A-COST-02** | *EU ETS carbon allowance price is $90/tonne CO2e with 100% surrender liability.* | **`EMPIRICALLY GROUNDED`** | European Energy Exchange (EEX) EUA futures; Directive (EU) 2023/959 2026 rules. | EUA prices fluctuate between $60$ and $110\text{ EUR/tonne}$. |
| **A-COST-03** | *Port demurrage penalty scales linearly at $1,000/hour beyond the hard deadline.* | **`HEURISTIC / ASSUMED`** | Standard commercial charter party terms (BIMCO GENCON). | Charter party contracts often have stepped or capped demurrage rates. |

### 2.4 Regulatory Compliance

| ID | Assumption Statement | Confidence Status | Empirical Basis / Provenance | Danger / Boundary Condition |
| :--- | :--- | :---: | :--- | :--- |
| **A-REG-01** | *FuelEU Maritime targets an 89.34 g CO2e/MJ Well-to-Wake intensity limit for 2025-2029.* | **`VALIDATED`** | Regulation (EU) 2023/1805, Annex I; 2% reduction below 91.16 baseline. | Non-EU territorial waters are exempt; extra-EU voyages carry 50% liability. |
| **A-REG-02** | *FuelEU statutory penalty is exactly 2,400 EUR per tonne VLSFO equivalent deficit.* | **`VALIDATED`** | Regulation (EU) 2023/1805, Article 23(2). | Applies strictly to verified compliance deficits after banking/pooling. |
| **A-REG-03** | *IMO CII annual reduction factor Z is 11% in 2026 for container and cruise vessels.* | **`VALIDATED`** | IMO Resolution MEPC.338(76) & MEPC.354(78). | Offshore supply vessels are not currently rated under MARPOL Annex VI Reg 28. |

### 2.5 Uncertainty & Metaheuristic Optimization

| ID | Assumption Statement | Confidence Status | Empirical Basis / Provenance | Danger / Boundary Condition |
| :--- | :--- | :---: | :--- | :--- |
| **A-OPT-01** | *QPSO operates as a classical quantum-inspired metaheuristic without physical quantum hardware.* | **`VALIDATED`** | Sun et al. (2004); strictly classical execution on CPU cores. | **STRICTLY PROHIBITED**: Claiming quantum advantage or quantum processing. |
| **A-OPT-02** | *Quantile pinball loss [q05, q95] represents operational prediction dispersion.* | **`VALIDATED`** | LightGBM quantile regression trained on FuelCast fleet. | Empirical coverage is $78.51\%$ (under-covering nominal $90\%$). Must not be labeled "90% confidence". |
| **A-OPT-03** | *SafeFuelObjective quadratic penalties guide swarm particles away from unphysical boundaries.* | **`VALIDATED`** | Repelled 100% of 8 tested adversarial boundary exploits in Phase 2.3. | Extremely large step sizes in DE/GA could occasionally jump across penalty boundaries if not clipped. |
