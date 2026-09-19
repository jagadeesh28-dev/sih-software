# PHASE 4 SCIENTIFIC ASSUMPTIONS & EVIDENCE LEDGER
**Project:** SIH26138 — Egreen Quanta: Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization  
**Stage:** Heterogeneous Fleet Optimization Scientific Assumptions & Epistemological Ledger  
**Date:** 2026-09-14  
**Status:** COMPLETE & AUDITED  

---

## 1. Epistemological Framework

In accordance with rigorous computational science and SIH26138 standards, every assumption in Phase 4 is cataloged and assigned an epistemological confidence rating:
- **`VALIDATED`**: Empirically demonstrated by real-world telemetry (`FuelCast` dataset) or verified numerical proof within this repository.
- **`EMPIRICALLY GROUNDED`**: Calibrated against established naval architecture literature (ITTC, IMO resolutions, DNV guidelines) and peer-reviewed maritime models.
- **`HEURISTIC / ASSUMED`**: Engineering assumption required for mathematical tractability, scenario definition, or economic simulation.
- **`DANGEROUS IF EXTRAPOLATED`**: Valid strictly within the calibrated operational domain; invalid or physically misleading if generalized.

---

## 2. Phase 4 Comprehensive Assumptions Ledger

### 2.1 Heterogeneous Fleet & Operational Demands

| ID | Assumption Statement | Confidence Status | Empirical Basis / Provenance | Danger / Boundary Condition |
| :--- | :--- | :---: | :--- | :--- |
| **A-FLEET-01** | *The fleet consists of three heterogeneous vessels calibrated directly on real FuelCast telemetry (`CPS_Poseidon`, `CPS_Triton`, `OSS_Ceto`).* | **`VALIDATED`** | Real-world high-frequency telemetry (173k+ records); separate physics+residual models trained per vessel class. | **DO NOT EXTRAPOLATE**: Three vessels do not represent global maritime fleet statistical diversity. |
| **A-FLEET-02** | *Operational cargo demands (Demands A, B, C) represent distinct commercial transport missions.* | **`HEURISTIC / ASSUMED`** | Synthetic operational scenarios parameterized to stress vessel capacity and assignment constraints. | Labeled `SYNTHETIC_OPERATIONAL_SCENARIO`; not derived from confidential commercial charter parties. |
| **A-FLEET-03** | *Vessels cannot cross-serve incompatible demand types (e.g. cruise ships cannot carry offshore deck equipment).* | **`VALIDATED`** | Naval architectural ship design and safety certifications (SOLAS Passenger vs Cargo). | Enforced via hard combinatorial rejection. |

---

### 2.2 Metocean Weather Scenarios & Robustness

| ID | Assumption Statement | Confidence Status | Empirical Basis / Provenance | Danger / Boundary Condition |
| :--- | :--- | :---: | :--- | :--- |
| **A-WEATH-01** | *Weather along the voyage is represented by four discrete scenarios: Calm ($H_s=0.5\text{m}$), Moderate ($1.5\text{m}$), Rough ($2.5\text{m}$), and Severe ($3.5\text{m}$).* | **`EMPIRICALLY GROUNDED`** | Metocean hindcast distributions for North Sea / Baltic / Mediterranean shipping lanes. | Stationarity assumed across voyage duration; dynamic spatio-temporal storms not simulated. |
| **A-WEATH-02** | *Wave height is strictly bounded to $H_s \le 3.5\text{ m}$ to stay within the surrogate's validated training domain.* | **`VALIDATED`** | DomainChecker envelope derived from FuelCast operational dataset (99.8th percentile). | Severe storm conditions ($H_s > 4.5\text{ m}$) are outside validated surrogate domain. |
| **A-WEATH-03** | *Distributional robustness is accurately captured via Conditional Value at Risk ($\text{CVaR}_{0.80}$).* | **`EMPIRICALLY GROUNDED`** | Rockafellar & Uryasev (2000) coherent risk measure; penalizes worst 20% scenario outcomes. | Assumes scenario probabilities ($p = [0.4, 0.3, 0.2, 0.1]$) reflect regional sea state frequencies. |

---

### 2.3 Alternative Fuels & Compatibility

| ID | Assumption Statement | Confidence Status | Empirical Basis / Provenance | Danger / Boundary Condition |
| :--- | :--- | :---: | :--- | :--- |
| **A-FUEL-01** | *Ammonia is prohibited on passenger cruise vessels due to acute human toxicity.* | **`VALIDATED`** | IMO IGF Code safety guidelines; toxic vapor dispersion risk in passenger spaces. | Permitted only on offshore industrial vessels (`OSS_Ceto`). |
| **A-FUEL-02** | *Volumetric energy density penalties reduce allowable cargo volume for alternative fuels.* | **`EMPIRICALLY GROUNDED`** | DNV Maritime Forecast to 2050 (tank volume ratios: 1.8x LNG, 2.3x Methanol, 2.7x Ammonia). | May overestimate impact if alternative fuel tanks are retrofitted on open deck spaces. |
| **A-FUEL-03** | *Shore power (OPS / cold-ironing) completely eliminates auxiliary emissions during port berth.* | **`VALIDATED`** | Port of Kiel / Gothenburg verified shore connection metering studies. | Assumes green grid electricity; life-cycle grid emission intensity varies by country. |

---

### 2.4 Computational Optimization & Statistics

| ID | Assumption Statement | Confidence Status | Empirical Basis / Provenance | Danger / Boundary Condition |
| :--- | :--- | :---: | :--- | :--- |
| **A-OPT-01** | *QPSO is a classical quantum-inspired heuristic running entirely on standard x86 CPU hardware.* | **`VALIDATED`** | Sun et al. (2004); strictly classical simulation of delta potential well wavefunctions. | **ABSOLUTE PROHIBITION**: Never claim quantum computing, QPU hardware, or quantum advantage. |
| **A-OPT-02** | *Precomputed 101-point speed grid calibration accelerates evaluations without loss of scientific accuracy.* | **`VALIDATED`** | Empirical maximum relative interpolation error $< 0.048\%$ across all speed-weather combinations. | Grid must encompass full involuntary speed loss range down to $0.5\text{ kn}$. |
| **A-OPT-03** | *Absolute engineering threshold $\epsilon = 10^{-5}$ USD is mandatory before statistical ranking.* | **`VALIDATED`** | Numerical precision of 64-bit IEEE 754 floating point arithmetic in multi-component objective sum. | Treating differences below $10^{-5}$ as non-zero manufactures artificial statistical p-values. |
| **A-OPT-04** | *Scalability benchmarks ($N \in \{5, 20, 50, 100\}$, $D \in \{30, 120, 300, 600\}$) represent synthetic algorithmic stress tests.* | **`VALIDATED`** | Labeled `SYNTHETIC_SCALABILITY_BENCHMARK`; generated by cloning vessel class profiles. | Must not be presented as real 100-vessel commercial enterprise fleets. |

---

## 3. Epistemological Safeguards & Scientific Boundaries

1. **No Cherry-Picking**: Negative or equivalent results are explicitly preserved. If classical Differential Evolution (DE) or PSO matches QPSO, this equivalence is reported as a primary scientific finding.
2. **Decomposed Objective Reporting**: Total objective $J$ is always broken down into physical fuel cost, carbon cost, shore power cost, demurrage, and penalty components to guard against penalty dominance.
3. **Hard Constraint Isolation**: Infeasible solutions are strictly segregated from Pareto fronts and final comparative rankings.
