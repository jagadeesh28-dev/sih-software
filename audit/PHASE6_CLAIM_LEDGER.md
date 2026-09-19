# PHASE 6: SCIENTIFIC CLAIM LEDGER
## SIH26138 — Egreen Quanta
**Audit Date:** 2026-09-19  
**Protocol Version:** `6.0-FROZEN`  
**Status:** `AUDITED & CERTIFIED`  

This ledger governs every scientific and engineering claim permitted in the Egreen Quanta documentation, repository, jury presentation, and final technical defense.

---

### Claim Summary Matrix

| ID | Claim Category | Target Claim | Empirical Evidence | Status |
|---|---|---|---|---|
| **C-01** | Baseline Reproduction | Model reproduces $R^2=0.9501$, $\text{MAE}=246.97\text{ kg/h}$ | `scripts/phase6_baseline_reproduce.py` | **`SUPPORTED`** |
| **C-02** | Hardware Infrastructure | Classical execution on CPU; no physical QPU | System audit & environment manifest | **`SUPPORTED`** |
| **C-03** | Quantum Advantage | Claims of quantum advantage / supremacy | Disclaimed by scientific protocol | **`PROHIBITED`** |
| **C-04** | QIEA Feature Selection | QIEA selects predictive hydrodynamic feature subsets | P4 vs P3 on 30 matched seeds | **`SUPPORTED`** |
| **C-05** | QIEA Search Diversity | Q-bit chromosome maintains higher initial entropy | $H(Q)$ trajectory & Hamming diversity | **`SUPPORTED`** |
| **C-06** | QPSO Hyperparameter Tuning | Delta-potential well tunes LightGBM parameters | P5 vs P4 & CPSO ablation | **`SUPPORTED`** |
| **C-07** | MPS Tensor Representation | Direct tensor network residual modeling | P6 vs Classical Polynomial Ridge | **`SUPPORTED`** |
| **C-08** | Cross-Vessel Generalization | Evaluated across 3 real vessels in FuelCast | 3-Fold Leave-One-Vessel-Out (LOVO) | **`CONDITIONALLY SUPPORTED`** |
| **C-09** | Operating Regimes | Evaluated on harbor, maneuvering, cruising, rough | Stratified regime error breakdown | **`SUPPORTED`** |
| **C-10** | Out-of-Distribution | Evaluates degraded telemetry via Mahalanobis bounds | Vectorized Mahalanobis distance test | **`SUPPORTED`** |
| **C-11** | Physical Consistency | Model satisfies $F \ge 0$ and STW monotonicity | Automated unit tests & bounds audit | **`SUPPORTED`** |
| **C-12** | Alternative Fuels | Scenario calculations for LNG, Methanol, Ammonia | Physics-based stoichiometric simulations | **`CONDITIONALLY SUPPORTED`** |
| **C-13** | Downstream Integration | Prediction feeds into CommonFleetEvaluator | DE downstream sensitivity test | **`SUPPORTED`** |

---

### Detailed Claim Ledger

#### CLAIM C-01: Baseline Exact Match
- **Statement:** The hybrid physics-ML residual model (`MODEL-REAL-04`) achieves $R^2 = 0.9501$, $\text{MAE} = 246.97\text{ kg/h}$, and $\text{MAPE} = 14.63\%$ under forward chronological testing.
- **Evidence:** Verified by `scripts/phase6_baseline_reproduce.py` on 173,974 FuelCast records.
- **Permitted Wording:** "The frozen baseline reproduces $R^2 = 0.9501$ and $\text{MAE} = 246.97\text{ kg/h}$ exactly to four decimal places."
- **Forbidden Wording:** "The baseline was tuned specifically for Phase 6."

#### CLAIM C-02: Classical Execution
- **Statement:** All quantum-inspired prediction and optimization methods execute on classical x86_64 CPU hardware without physical quantum devices.
- **Evidence:** Python 3.14 on Windows 11 host with NumPy/SciPy/LightGBM.
- **Permitted Wording:** "All quantum-inspired mechanisms are classical algorithms inspired by quantum state mathematics."
- **Forbidden Wording:** "Executed on quantum computer", "QPU accelerated", "Quantum tunneling observed".

#### CLAIM C-03: Quantum Advantage / Speedup
- **Statement:** Egreen Quanta does not claim physical quantum advantage or exponential speedup.
- **Evidence:** Theoretical and empirical runtime benchmarks demonstrate classical polynomial complexity.
- **Permitted Wording:** "Quantum-inspired algorithms provide alternative search trajectories on classical hardware."
- **Forbidden Wording:** "Quantum advantage demonstrated", "Exponential quantum speedup achieved".

#### CLAIM C-04: QIEA Feature Selection (`QI-C1`)
- **Statement:** QIEA feature selection isolates predictive hydrodynamic features via Q-bit rotation gates.
- **Evidence:** `results/tables/phase6_qi_ablation.csv` and 30-seed Wilcoxon signed-rank tests.
- **Permitted Wording:** "QIEA feature selection identifies compact, physically consistent feature subsets on validation loss under equal evaluation budgets."
- **Forbidden Wording:** "QIEA exponentially outperforms all classical genetic algorithms."

#### CLAIM C-05: QIEA Diversity & Entropy
- **Statement:** Q-bit representation maintains high initial Shannon entropy ($H \approx 1.0$), enabling broader combinatorial exploration prior to rotation-gate collapse.
- **Evidence:** Entropy trajectory audits in `results/tables/phase6_prediction_comparison.csv`.
- **Permitted Wording:** "Q-bit chromosomes exhibit higher search diversity and population entropy during early search iterations."
- **Forbidden Wording:** "Quantum superposition physically simultaneously explores all $2^N$ states."

#### CLAIM C-06: QPSO Hyperparameter Optimization (`QI-C2`)
- **Statement:** Delta-potential well QPSO tunes LightGBM hyperparameters and coupling parameter $\alpha$.
- **Evidence:** Matched comparison against Classical PSO and Random Search under 150 evaluations.
- **Permitted Wording:** "QPSO optimizes continuous hyperparameters via delta-potential bound-state mechanics."
- **Forbidden Wording:** "Particles tunnel through classical local minima via physical quantum effects."

#### CLAIM C-07: Direct QI Matrix Product State (`QI-C3`)
- **Statement:** A direct tensor-network residual predictor operates on trigonometric quantum feature maps $\phi(x) = [\cos(\pi x / 2), \sin(\pi x / 2)]^T$.
- **Evidence:** Tensor contraction with bond dimension $\chi=4$ evaluated against classical polynomial expansion.
- **Permitted Wording:** "A compact Matrix Product State tensor network factorizes high-dimensional interactions over trigonometric feature mappings."
- **Forbidden Wording:** "Tensor network implements quantum circuit simulation on NISQ hardware."

#### CLAIM C-08: Cross-Vessel Generalization
- **Statement:** The models are evaluated under Leave-One-Vessel-Out (LOVO) across the three available FuelCast ships.
- **Evidence:** `results/tables/phase6_lovo_results.csv`.
- **Permitted Wording:** "Cross-vessel transfer is evaluated across the three available real vessels (Poseidon, Triton, Ceto)."
- **Forbidden Wording:** "Validated for universal, fleet-wide generalization across all global commercial shipping."

#### CLAIM C-09: Operating Regimes
- **Statement:** Model accuracy is characterized across distinct operating regimes (Cruising, Maneuvering, Harbor, Rough Sea).
- **Evidence:** Stratified error breakdown in `results/tables/phase6_regime_breakdown.csv`.
- **Permitted Wording:** "Prediction accuracy is stratified across four operational regimes derived from telemetry velocity and environmental data."
- **Forbidden Wording:** "Zero performance degradation in extreme sea states."

#### CLAIM C-10: Out-of-Distribution Robustness
- **Statement:** Telemetry observations outside the dense training envelope are identified using Mahalanobis distance.
- **Evidence:** In-distribution vs. Out-of-distribution error analysis.
- **Permitted Wording:** "Mahalanobis distance bounds quantify prediction degradation on out-of-distribution operational states."
- **Forbidden Wording:** "Model is immune to distribution shift."

#### CLAIM C-11: Physical Consistency
- **Statement:** The prediction pipeline strictly satisfies non-negativity ($\hat{y} \ge 0$) and calm-water speed monotonicity ($dF / dv > 0$).
- **Evidence:** 19/19 unit tests passing in `tests/test_physics_constraints.py`.
- **Permitted Wording:** "Physical lower bounds and hydrodynamic monotonicity are strictly enforced by the hybrid physics prior."
- **Forbidden Wording:** "Complete hydrodynamic fluid dynamics Navier-Stokes closure achieved."

#### CLAIM C-12: Alternative Fuels Scenarios
- **Statement:** Alternative-fuel consumption (LNG, Methanol, Ammonia, Hydrogen) is generated via naval architecture thermodynamic energy equivalence ($LHV_f$ and $\eta_f$), clearly separated from real measured diesel telemetry.
- **Evidence:** Explicit scenario assumptions in `configs/phase6_baseline.yaml`.
- **Permitted Wording:** "Alternative-fuel figures represent physics-based scenario simulations derived from lower heating values."
- **Forbidden Wording:** "Real measured alternative-fuel engine telemetry."

#### CLAIM C-13: Downstream Fleet Optimizer Sensitivity
- **Statement:** Prediction differences are propagated into `CommonFleetEvaluator` to measure their direct effect on fleet-level decision support.
- **Evidence:** Controlled downstream DE optimization test in `experiments/run_phase6_downstream_integration.py`.
- **Permitted Wording:** "Upstream prediction variations produce quantifiable shifts in fleet fuel, cost, and Pareto front decisions."
- **Forbidden Wording:** "Prediction differences completely overturn fleet optimization decisions."
