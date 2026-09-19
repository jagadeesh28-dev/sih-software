# PHASE 4 — PRE-IMPLEMENTATION AUDIT & BASELINE FREEZE

**Project:** SIH26138 — Egreen Quanta: Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization  
**Phase:** Phase 4 Pre-Implementation Audit  
**Date:** 2026-09-14  
**Audit Author:** Independent Scientific & Optimization Auditor  

---

## 1. Baseline Freeze Statement

> [!IMPORTANT]
> **IMMUTABILITY DECLARATION:**  
> All historical findings, raw data, statistical analysis, and figures from Phase 3.2 and Phase 3.2.1 are **FROZEN AND IMMUTABLE**.  
> The following directories shall NEVER be modified or overwritten:
> - `results/experiments/optimization_phase3_2/`
> - `results/audit/phase3_2/`
> - `results/audit/phase3_2_1/`
> - `results/figures/optimization_phase3_2/`
> - `results/figures/optimization_phase3_2_1/`  
> 
> All Phase 4 experimental benchmarks, audit artifacts, and visualization plots will reside strictly within isolated Phase 4 namespaces:
> - `results/experiments/optimization_phase4/`
> - `results/audit/phase4/`
> - `results/figures/optimization_phase4/`

---

## 2. System & Codebase State at Phase 4 Entry

| Parameter | Recorded State | Verification Source |
| :--- | :--- | :--- |
| **Git Commit Hash** | `20309b214b9540a7363b7365e442a222cd9c49a1` | `git log -n 1 --oneline` |
| **Branch** | `master` | `git status` |
| **Operating System** | Windows 11 (AMD64) | `platform.platform()` |
| **CPU Architecture** | Intel64 Family 6 Model 183 (20 logical cores) | `os.cpu_count()` |
| **Python Version** | Python 3.14.0 | `sys.version` |
| **NumPy Version** | 2.2.3 | `numpy.__version__` |
| **Pandas Version** | 2.2.3 | `pandas.__version__` |
| **SciPy Version** | 1.15.2 | `scipy.__version__` |
| **Pytest Version** | 9.1.1 | `pytest.__version__` |
| **Matplotlib Version** | 3.10.1 | `matplotlib.__version__` |
| **LightGBM Version** | 4.6.0 | `lightgbm.__version__` |
| **Regression Test Suite** | **97 passed, 0 failed** in 90.90s | `pytest tests/ -q` |

---

## 3. Summary of Phase 3.2.1 Scientific Audit Findings

Phase 3.2.1 conducted an independent statistical integrity audit of the Phase 3.2 benchmark (150 runs, 5 optimizers, 30 matched seeds, 2,500 evaluations/run, 375,000 total evaluations) and reached the following definitive verdicts:

1. **Resolution of the Wilcoxon Anomaly:**
   - Phase 3.2 reported `ties = 30, wins = 0, losses = 0, Wilcoxon stat = 81.0, p = 0.00123, is_sig = True` for QPSO vs DE.
   - Root-cause: The raw difference array passed to `scipy.stats.wilcoxon` contained machine-precision floating-point noise ($|\Delta J| \sim 10^{-7}\text{ to }10^{-9}$) caused by non-consequential cargo allocation variations on passenger cruise vessels.
   - When thresholded at domain precision ($|\Delta J| \le 10^{-5}$), $n_{\text{nonzero}} = 0$, Wilcoxon is **NOT APPLICABLE ($p = 1.0000$)**, and an independent 100,000-resample permutation test confirmed **$p = 1.0000$**.
   - **Verdict:** QPSO and DE are **mathematically tied at the exact same physical optimum ($J = 3.2758$)**. QPSO superiority is withdrawn.

2. **Benchmark Difficulty Classification:**
   - In 10,000 uniform unguided random evaluations on SCEN-01, the best candidate was within **$0.0009$ ($0.027\%$)** of the metaheuristic optimum.
   - The landscape is a smooth, convex, single-basin attractor where the deadline speed ($18.59\text{ kn}$) and regulatory fuel dominance (bio-methanol) collapse the decision space.
   - **Verdict:** SCEN-01 is **EASY**.

3. **High-Dimensional Scalability ($D=500$, 100 Vessels):**
   - Under $N=200$ evaluations, QPSO achieved $J = 1.20 \times 10^6$ vs DE $2.54 \times 10^6$ ($2.1\times$ to $2.36\times$ ratio).
   - However, theoretical unpenalized loss is $\sim 328$. Both algorithms were **99.97% penalty-dominated**.
   - **Verdict:** QPSO reduces synthetic schedule penalties faster than DE under extreme budget starvation, but this does **not** represent $2.36\times$ lower fuel consumption. Classified as **PROVISIONAL (SYNTHETIC ONLY)**.

4. **Phase 3.2.1 Gate Verdict:**
   - **SCIENTIFIC STATUS:** `CONDITIONAL PASS`
   - **PHASE 4 READY:** `YES WITH CLAIM RESTRICTIONS`

---

## 4. Current Platform Components & Baselines

### 4.1 Real-Data Surrogates (`SafeFuelObjective`)
- Trained on FuelCast real high-frequency telemetry:
  - `CPS_Poseidon`: Passenger Cruise ship (`passenger_cruise`)
  - `CPS_Triton`: Small Passenger Cruise ship (`passenger_cruise_small`)
  - `OSS_Ceto`: Offshore Supply Vessel (`offshore_supply`)
- Architecture: Pure ML LightGBM/XGBoost residual predictor + Quantile uncertainty predictor + Holtrop-Mennen/ISO 15016 physics base model + 14-channel `DomainChecker`.
- Baseline Validation: $R^2 \ge 0.88$ on holdout test segments within the operational envelope.

### 4.2 Current Objective Function Formulation
$$J(x) = \sum_{k=1}^5 w_k \left(\frac{f_k(x)}{s_k}\right) + \sum \text{penalties}$$
- $w = [0.35, 0.30, 0.25, 0.05, 0.05]$ for Fuel, Cost, GHG, Delay, and Risk.
- Normalization Scales: $s = [50.0\text{ t}, 50,000\text{ USD}, 150.0\text{ t}, 10.0\text{ h}, 15.0\text{ t}]$.
- Domain Barrier Penalty: $+100,000$ for out-of-domain states; soft quadratic penalty for schedule delays.

### 4.3 Regulatory Framework
- **FuelEU Maritime (EU 2023/1805):** Reference GHG target $91.16\text{ gCO}_2\text{e/MJ}$, compliance deficit penalty $2,400\text{ EUR/t VLSFO-equivalent}$.
- **CII (IMO MARPOL Annex VI):** Evaluated strictly on annual basis; single voyages receive modeled operational emissions reporting without false non-compliance penalties.

### 4.4 Metaheuristic Implementations
- **QPSO:** Quantum delta-potential well attractor with contraction-expansion parameter $\beta(t) \in [0.5, 1.0]$.
- **DE:** Canonical DE/rand/1/bin with greedy selection, $F=0.8, CR=0.9$.
- **PSO:** Clerc constriction factor $\chi \approx 0.7298, c_1=c_2=2.05$.
- **GA:** Tournament selection, simulated binary crossover (SBX $\eta_c=2.0$), polynomial mutation ($\eta_m=20.0$).
- **Random Search:** Uniform bounded pseudo-random hypercube sampling.

---

## 5. Required Phase 4 Transitions

To overcome the limitations documented in Phase 3.2.1, Phase 4 must execute the following structural advancements:

1. **Replace Single-Vessel SCEN-01 with a Real Heterogeneous Fleet:**
   - Concurrently deploy `CPS_Poseidon`, `CPS_Triton`, and `OSS_Ceto`.
2. **Introduce Non-Interchangeable Cargo Demands:**
   - 3 distinct transport demands (Luxury cruise tour, Coastal eco-expedition, Offshore energy deck cargo) requiring combinatorial matching.
3. **Incorporate Environmental Uncertainty & CVaR Risk:**
   - 4 discrete weather scenarios (Calm, Moderate, Rough, Severe) evaluated under Conditional Value at Risk ($\text{CVaR}_{0.80}$) with risk-aversion sweeps $\lambda \in [0.0, 1.0]$.
4. **Implement Strict Fuel Compatibility Matrices:**
   - Enforce engineering and SOLAS constraints preventing arbitrary alternative fuel use (e.g. prohibiting toxic Ammonia or cryogenic LNG on passenger ships).
5. **Establish Genuinely Difficult Search Landscapes:**
   - Target a random search feasibility rate $< 25\%$ and objective gap $> 10\%$, ensuring the optimization challenge cannot be trivially solved.
6. **Maintain Absolute Statistical Rigor:**
   - 30 matched seeds, 100,000-resample permutation tests, Holm-Bonferroni multiple comparison corrections, and strict separation between statistical significance and operational magnitude.

---

*Signed and Certified:*  
**Lead Auditor, Phase 4 Pre-Implementation Review**  
*SIH26138 Platform Governance Committee*
