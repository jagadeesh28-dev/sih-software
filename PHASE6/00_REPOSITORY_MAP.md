# PHASE 6 REPOSITORY MAP & SCIENTIFIC ARCHITECTURE AUDIT
## SIH26138 — Egreen Quanta
### Quantum-Inspired Fuel Consumption Prediction Research, Implementation & Scientific Validation

**Date:** September 19, 2026  
**Lead Research Engineers:** ML Research Scientist, Quantum-Inspired Computing Researcher, Maritime Propulsion Specialist, Time-Series Validation Scientist, Scientific Code Auditor  
**Phase Status:** PHASE 6 INITIALIZATION & AUDIT  

---

## 1. Executive Overview & Scientific Directive

Phase 5 heterogeneous fleet optimization has been conclusively audited, verified, and **FROZEN** (Status: `PASS`, see [PHASE5_STATUS.md](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/PHASE5_STATUS.md)).
The objective of Phase 6 is to resolve the central scientific question:

> **"Can a genuinely quantum-inspired prediction mechanism predict maritime fuel consumption accurately on real multi-vessel telemetry, and does it provide measurable value compared with a strong classical physics + ML residual baseline?"**

As mandated by scientific discipline:
- Possible outcomes are:
  - **Outcome A:** QI prediction clearly outperforms the classical baseline.
  - **Outcome B:** QI prediction is statistically comparable but offers another useful property (diversity, robustness, uncertainty calibration, compactness, search efficiency).
  - **Outcome C:** QI prediction is competitive but not superior.
  - **Outcome D:** QI prediction fails.
- All four outcomes are scientifically acceptable. Experiments will **never** be manipulated to force Outcome A.
- Phase 5 fleet optimization algorithms, evaluation budgets, and constraints remain **strictly immutable**.
- Terminology rule strictly enforced: Only **"quantum-inspired"** or **"classical quantum-inspired algorithm"**. Strictly forbidden: *"quantum computing"*, *"quantum hardware"*, *"quantum advantage"*, *"quantum speedup"*, *"qubit processor"*.

---

## 2. Comprehensive Repository Inventory

| File / Component Path | Purpose / Description | Primary Dependencies | Input Data / Features | Output Artifacts | Freeze Status | Modification Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Telemetry & Data Assets** | | | | | | |
| `data/processed/real/fuelcast/CPS_Poseidon.parquet` (25.7 MB) | Real 1-minute telemetry for container feeder *CPS_Poseidon* (105,422 rows) | `pyarrow`, `pandas` | Raw Coriolis mass flow, STW, SOG, draft, metocean | Clean canonical dataframe | **FROZEN** | Read-Only |
| `data/processed/real/fuelcast/CPS_Triton.parquet` (7.5 MB) | Real 1-minute telemetry for container feeder *CPS_Triton* (25,347 rows) | `pyarrow`, `pandas` | Raw Coriolis mass flow, STW, SOG, draft, metocean | Clean canonical dataframe | **FROZEN** | Read-Only |
| `data/processed/real/fuelcast/OSS_Ceto.parquet` (10.3 MB) | Real 1-minute telemetry for Handymax bulk vessel *OSS_Ceto* (43,205 rows) | `pyarrow`, `pandas` | Raw Coriolis mass flow, STW, SOG, draft, metocean | Clean canonical dataframe | **FROZEN** | Read-Only |
| `scratch/phys_*.npy` & `physics_cache.npz` | Precomputed static physics predictions for all 173,986 rows | `numpy` | Hydrodynamic STW + resistance pipeline | Cached physics fuel predictions (kg/h) | **REUSABLE** | Maintained / Verified |
| **Physics Propulsion Models** | | | | | | |
| `physics/resistance_model.py` | Complete naval architecture resistance pipeline ($R_{total} = R_{calm} + R_{wave} + R_{wind}$) | `numpy`, `scipy` | STW (kn), draft, displacement, wind, waves | Total resistance (N), Effective Power ($P_E$) | **FROZEN** | Read-Only |
| `physics/propulsion.py` | Propulsion efficiency chain ($P_E \to P_D \to P_B \to \text{Fuel}$) | `physics/` | $R_{total}$, speed, wake fraction, thrust deduction | Shaft power ($P_B$, kW), SFC (g/kWh), fuel (kg/h) | **FROZEN** | Read-Only |
| `physics/holtrop_mennen.py` | Calm-water bare hull resistance implementation | `numpy` | Length, beam, draft, prismatic coefficient, STW | $R_F, R_{APP}, R_W, R_B, R_{TR}, R_A$ | **FROZEN** | Read-Only |
| `physics/wind_resistance.py` | Aerodynamic drag model (Blendermann / Isherwood) | `numpy` | Relative wind speed, relative wind angle, transverse area | Wind added resistance (N) | **FROZEN** | Read-Only |
| `physics/stawave2.py` | Added resistance in waves (IMO STAwave-2 semi-empirical) | `numpy` | Significant wave height ($H_s$), wave period ($T_z$), heading | Wave added resistance (N) | **FROZEN** | Read-Only |
| `prediction/physics_predictor.py` | Interface wrapping physics pipeline; enforces STW constraint | `physics/` | DataFrame with `stw_kn` + metocean | Vectorized fuel flow predictions (kg/h) | **FROZEN** | Read-Only |
| **Classical Baselines & Residual Models** | | | | | | |
| `prediction/residual_model.py` | Hybrid Residual Learner ($F(x) = \max(0, F_{phys}(x) + \alpha \cdot \hat{r}(x))$) | `lightgbm`, `sklearn` | Training residual $r = y - F_{phys}$, `CONFIG_REAL_A` | Fitted hybrid predictor | **FROZEN** | Benchmark Anchor |
| `prediction/ml_baseline.py` | Pure classical ML baseline models (LightGBM, Random Forest, MLP) | `lightgbm`, `sklearn` | `CONFIG_REAL_A` / `CONFIG_REAL_B` | Direct fuel predictions | **FROZEN** | Benchmark Anchor |
| `prediction/domain_checker.py` | Feature space bounding box and Mahalanobis domain guardian | `scipy`, `numpy` | Multi-vessel feature distributions | In-domain boolean mask, OOD penalty | **REUSABLE** | Used in Deployment Guard |
| `prediction/evaluate.py` | Common evaluation metrics (MAE, RMSE, MAPE, $R^2$, MedianAE, MaxAE) | `numpy`, `scipy` | $y_{true}$, $y_{pred}$ | Comprehensive error metrics dictionary | **FROZEN** | Evaluation Engine |
| `prediction/quantile_model.py` | Empirical quantile regression for predictive interval calibration | `lightgbm`, `numpy` | Residual features | Quantile predictions ($\alpha \in [0.05, 0.95]$) | **REUSABLE** | Uncertainty Engine |
| **Quantum-Inspired Prediction Stack (Phase 6)** | | | | | | |
| `src/qi_prediction/qiea.py` | Quantum-Inspired Evolutionary Algorithm with Q-bit rotation gates | `numpy` | Feature subset search space, evaluation closure | Optimized feature mask, Q-bit diversity entropy | **NEW / ACTIVE** | Verified & Benchmark Ready |
| `src/qi_prediction/qpso.py` | Delta-potential well Quantum-Behaved PSO + classical controls | `numpy` | Continuous hyperparameter search space | Optimal model hyperparameters, convergence log | **NEW / ACTIVE** | Verified & Benchmark Ready |
| `src/qi_prediction/mps_predictor.py` | Tensor-Network Matrix Product State (MPS) residual predictor | `numpy`, `sklearn` | Bounded feature map $\phi(x) = [\cos, \sin]^T$ | Contracted tensor predictions ($r_{MPS}$) | **NEW / ACTIVE** | Verified & Benchmark Ready |
| `src/qi_prediction/feature_selection.py` | Classical Genetic Algorithm & random feature selection controls | `numpy`, `random` | Identical evaluation budget (150 evals) | Classical baseline feature masks | **NEW / ACTIVE** | Matched Control |
| `src/qi_prediction/validation.py` | Time-series validation harness (LOVO, rolling origin, regime, OOD) | `pandas`, `scipy` | Telemetry partitions | Multi-split validation metrics | **NEW / ACTIVE** | Validation Engine |
| `src/qi_prediction/statistics.py` | Statistical significance engine (paired Wilcoxon, Holm, Hodges-Lehmann) | `scipy.stats`, `numpy`| 30-seed matched metric arrays | p-values, rank-biserial effect sizes, bootstrap CIs | **NEW / ACTIVE** | Statistical Engine |
| `src/qi_prediction/benchmark.py` | Master 30-seed benchmarking pipeline across P0–P7 | `src/qi_prediction/` | Telemetry, 30 matched seeds (1001–1030) | Full CSV tables, ablation, figures | **NEW / ACTIVE** | Main Pipeline Runner |
| **Phase 5 Frozen Optimization Assets** | | | | | | |
| `optimization/fleet_evaluator_phase4.py` | Canonical multi-scenario fleet simulation & physical constraints | `optimization/` | Route assignments, speed profiles, weather | Multi-objective vector (fuel, opex, GHG, delay) | **FROZEN** | Strictly Untouchable |
| `src/evaluator/common_evaluator.py` | Unified evaluator interface with Hungarian deterministic repair | `src/evaluator/` | Particle vectors | Constraint-evaluated fitness | **FROZEN** | Strictly Untouchable |
| `src/algorithms/de.py` | Benchmark Differential Evolution fleet optimizer | `numpy` | Fleet decision variables | Optimized fleet schedules & Pareto fronts | **FROZEN** | Downstream Integration |
| `experiments/run_phase6_downstream_integration.py` | Downstream impact test: feeding QI vs Classical predictors into fleet optimizer | `optimization/`, `src/` | Predicted fuel surrogates | Schedule impact, Pareto frontier shift | **NEW / ACTIVE** | Integration Test |
| **Configuration Files** | | | | | | |
| `configs/phase6_baseline.yaml` | Specification of frozen MODEL-REAL-04 baseline | YAML | Split, features, hyperparameters, targets | Parameter provenance | **NEW / ACTIVE** | Config Specification |
| `configs/phase6_qi.yaml` | Formal mathematical specification of QIEA, QPSO, and MPS | YAML | Hyperparameter bounds, Q-bit rotations | Algorithmic parameter ledger | **NEW / ACTIVE** | Config Specification |
| `configs/phase6_benchmark.yaml` | Complete 30-seed matched benchmark execution matrix | YAML | Seeds, models (P0–P7), validation splits | Master run orchestration | **NEW / ACTIVE** | Config Specification |

---

## 3. Seven Specific Audit Answers

### 1. What already exists?
- Full 173,986 real-world commercial vessel telemetry records across 3 vessels (*CPS_Poseidon*, *CPS_Triton*, *OSS_Ceto*) with high-frequency Coriolis mass-flow meters.
- First-principles naval architecture physics pipeline locked to Speed Through Water (STW) via Holtrop-Mennen, STAwave-2, and Blendermann aerodynamic drag.
- Documented, verified classical baseline `MODEL-REAL-04 (Hybrid Residual)` achieving $R^2 \approx 0.9501$, $\text{MAE} \approx 246.97\text{ kg/h}$, $\text{MAPE} \approx 14.63\%$.
- Frozen Phase 5 multi-objective fleet optimization engine (`CommonFleetEvaluator`, Hungarian repair, Deb's feasibility-first constraint handling, DE/A5 algorithms).
- Complete modular implementation of Quantum-Inspired prediction modules: `QIEAFeatureSelector` (Q-bit rotation gates), `QPSOOptimizer` (delta-potential well bound states), `QIMPSPredictor` (Matrix Product State tensor network on trigonometric feature map), and budget-matched classical controls.

### 2. What is frozen?
- **Phase 5 Fleet Optimization Layer:** `optimization/fleet_evaluator_phase4.py`, `src/evaluator/common_evaluator.py`, `optimization/constraints.py`, `optimization/regulatory.py`.
- **Target Variable & Split Protocol:** Target `fuel_mass_flow_kg_h` measured directly via Coriolis flow meters; strict chronological forward temporal split (60% Train, 20% Val, 20% Test) per vessel.
- **Physics Propulsion Model:** `physics/resistance_model.py`, `physics/propulsion.py`, `prediction/physics_predictor.py`. STW is strictly mandatory; substitution of SOG is forbidden.
- **Reference Baseline:** `MODEL-REAL-04` ($R^2 = 0.9501, \text{MAE} = 246.97\text{ kg/h}$) recorded in `08_REAL_MODEL_RESULTS.csv`.

### 3. What can be reused?
- Real FuelCast telemetry parquets in `data/processed/real/fuelcast/`.
- Precomputed physics prediction arrays in `scratch/phys_*.npy` to accelerate repeated 30-seed model evaluations.
- `ValidationHarness` in `src/qi_prediction/validation.py` for LOVO, rolling origin, regime stratification, and Mahalanobis OOD detection.
- `PredictionStatisticsEngine` in `src/qi_prediction/statistics.py` for paired Wilcoxon, Holm-Bonferroni, and Hodges-Lehmann testing.
- `DomainChecker` and `QuantileUncertaintyPredictor` for domain guarding and predictive interval calibration.

### 4. What must be implemented / compiled in Phase 6?
- **Reproduce Baseline & Verify Freeze:** Verify that running `MODEL-REAL-04` produces exact metrics ($R^2 \approx 0.9501, \text{MAE} \approx 246.97, \text{MAPE} \approx 14.63\%$).
- **Complete Audit Documentation in `PHASE6/`:**
  - 19 numbered markdown scientific reports (`00_REPOSITORY_MAP.md` through `19_FINAL_SIH_STORY.md`).
  - 14 core CSV results tables in `PHASE6/results/tables/` and `PHASE6/results/statistics/`.
  - Minimum 16 publication figures in `PHASE6/results/figures/`.
  - Configuration specifications in `PHASE6/config/` (`baseline.yaml`, `qi_c1.yaml`, `qi_c2.yaml`, `normalization.json`).
  - Formal scientific reports in `PHASE6/reports/` (`PHASE6_FINAL_SCIENTIFIC_REPORT.md`, `PHASE6_CLAIM_LEDGER.yaml`, `PHASE6_EXECUTIVE_SUMMARY.md`).
- **Downstream Optimization Experiment:** Feeding classical vs QI predictors into the frozen Phase 5 fleet optimizer to measure downstream schedule, fuel, and Pareto shifts.

### 5. What must NOT be changed?
- The Phase 5 fleet optimization algorithm, constraints, penalties, or evaluation budgets.
- The 14-feature definition of `CONFIG_REAL_A` (strictly hydrodynamic & metocean; machinery power/RPM/torque excluded to avoid operational leakage).
- The random seed set for the 30 matched runs (Seeds: 42, 1001–1029).
- The evaluation budget for metaheuristic searches: exactly 150 evaluations for QIEA (10 pop $\times$ 15 gen) matched against Classical GA (150 evals); exactly 150 evaluations for QPSO (15 particles $\times$ 10 iter) matched against Classical PSO and Random Search.

### 6. Exact files you will modify / create:
- **Create New:**
  - `PHASE6/00_REPOSITORY_MAP.md` (this file)
  - `PHASE6/01_BASELINE_REPRODUCTION.md`
  - `PHASE6/02_DATA_LEAKAGE_AUDIT.md`
  - `PHASE6/03_DATA_CHARACTERIZATION.md`
  - `PHASE6/04_PHYSICS_MODEL_AUDIT.md`
  - `PHASE6/05_CLASSICAL_BASELINES.md`
  - `PHASE6/06_QI_C1_DESIGN.md`
  - `PHASE6/07_QI_C2_MPS_DESIGN.md`
  - `PHASE6/08_VALIDATION_PROTOCOL.md`
  - `PHASE6/09_STATISTICAL_PROTOCOL.md`
  - `PHASE6/10_FAILURE_ANALYSIS.md`
  - `PHASE6/11_UNCERTAINTY_ANALYSIS.md`
  - `PHASE6/12_OOD_ANALYSIS.md`
  - `PHASE6/13_ALTERNATIVE_FUEL_SCENARIOS.md`
  - `PHASE6/14_PREDICTION_OPTIMIZER_INTEGRATION.md`
  - `PHASE6/15_NOVELTY_AUDIT.md`
  - `PHASE6/16_SIH_CLAIM_AUDIT.md`
  - `PHASE6/17_FINAL_SCIENTIFIC_VERDICT.md`
  - `PHASE6/18_FINAL_ARCHITECTURE_DECISION.md`
  - `PHASE6/19_FINAL_SIH_STORY.md`
  - `PHASE6/config/baseline.yaml`
  - `PHASE6/config/qi_c1.yaml`
  - `PHASE6/config/qi_c2.yaml`
  - `PHASE6/config/normalization.json`
  - All 14 core CSV files in `PHASE6/results/`
  - Master reports and claim ledger in `PHASE6/reports/`
- **Modify / Augment (Non-Breaking):**
  - None of Phase 5 files will be modified.

### 7. Exact experiments you will run:
1. **Experiment 6.1 — Baseline Forensic Reproduction:** Run `MODEL-REAL-04` on the 173,986 record FuelCast dataset under chronological split. Confirm MAE 246.97 kg/h, MAPE 14.63%, $R^2$ 0.9501.
2. **Experiment 6.2 — Data Leakage & Feature Provenance Audit:** Verify zero target leakage, temporal preservation, and isolation of scaling parameters to training folds.
3. **Experiment 6.3 — Classical Control Benchmark:** Evaluate Physics-Only (P0), Pure ML (P1), and Physics + ML Residual (P2).
4. **Experiment 6.4 — Candidate QI-C1 (QIEA-FS + QPSO-HPO) Benchmark:** Execute 30 matched seed runs for QIEA feature selection and QPSO hyperparameter optimization.
5. **Experiment 6.5 — Candidate QI-C2 (Direct Tensor Network / MPS) Benchmark:** Evaluate Matrix Product State predictor on trigonometric feature map across 30 seeds.
6. **Experiment 6.6 — Controlled Ablation Ladder (A0–A6):** Compare classical feature selection (A1) vs QIEA (A2) vs QIEA without rotation (A3); compare classical PSO vs QPSO (A4); compare MPS (A5) vs classical polynomial expansion (A6).
7. **Experiment 6.7 — Temporal & Cross-Vessel Generalization Stress Tests:** Forward temporal test, 3-window rolling origin, and 3-fold Leave-One-Vessel-Out (LOVO).
8. **Experiment 6.8 — Operational Regime & Out-of-Distribution Stress Tests:** Evaluate performance across Cruising, Maneuvering, Stopped, and Rough Sea regimes; test degradation under Mahalanobis distance OOD ($>95$th percentile).
9. **Experiment 6.9 — Uncertainty Calibration & Failure Mode Analysis:** Evaluate prediction interval coverage (PICP at 80%, 90%, 95%), interval width (MPIW), and classify residual failure modes (F1–F7).
10. **Experiment 6.10 — Downstream Phase 5 Optimizer Integration:** Feed classical and QI predictor surrogates into the Phase 5 fleet evaluator and measure schedule delay, fleet fuel, and Pareto frontier impacts.
