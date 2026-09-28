# Phase 2 Completion Report — SIH26138: Egreen Quanta Platform
**Phase 2 / Phase 2.1: Physics-Informed Fuel Consumption Prediction Engine & Evidence Hardening Pass**  
**Execution Timestamp:** 2026-09-12T19:57:30Z  
**Software Version:** 0.2.1 (Phase 2.1 Evidence Hardened)  
**Git Commit:** `3a6d4e2b50e59740c933d86cfda7ba0779b2d485`  
**Platform Tests:** 53/53 PASSED  

---

## 1. Prediction Task Definition
The primary Phase 2 prediction task is strictly defined as:
$$\text{ESTIMATE INSTANTANEOUS FUEL MASS FLOW AT OBSERVATION TIME } t: \quad X(t) \to F(t)$$
- **Target Channel**: `fuel_mass_flow_kg_h` $(\text{kg/h})$.
- **Scope**: Synchronous operational estimation mapping instantaneous navigational, environmental, and propulsion variables observed at time $t$ to fuel mass flow at the identical timestamp $t$.
- **Boundary Distinction**: This is strictly an operational state estimation problem, **NOT an independent future forecasting problem** ($X(t) \to F(t+\Delta t)$). All predictor variables correspond to timestamp $t$. No claims of voyage forecasting, next-hour prediction, or forward lookahead are made for the Phase 2 models.

---

## 2. Architecture
The prediction architecture consists of four distinct, progressively evaluated model classes:
1. **Baseline 1 — Physics-Only (`PhysicsFuelPredictor`)**: First-principles naval architecture pipeline:
   $$\text{stw\_kn} \to R_{\text{calm}} \to R_{\text{wave}} \to R_{\text{wind}} \to R_T \to P_E \to P_D \to P_B \to \text{SFC} \to \hat{F}_{\text{phys}}$$
2. **Baseline 2 — ML-Only (`PureMLPredictor`)**: Direct gradient-boosted decision tree (LightGBM regressor) mapping operational, environmental, and engine features directly to fuel mass flow:
   $$\hat{F}_{\text{ML}} = f(X)$$
3. **Model 3 — Physics + ML Residual (`HybridResidualPredictor`)**: Residual decomposition modeling discrepancy between observed fuel rate and the physical prediction:
   $$r_i = F_{\text{obs}, i} - F_{\text{phys}, i}, \quad \hat{r} = f_{\text{ML}}(X), \quad \hat{F} = \max(0, F_{\text{phys}} + \alpha \cdot \hat{r})$$
   where $\alpha \in [0.0, 1.0]$ is tuned strictly on the validation partition.
4. **Model 4 — Physics + ML Residual + QPSO Model Selection (`QPSOModelSelector`)**: Classical offline quantum-inspired metaheuristic optimizing 8 hyperparameters against validation MAE under an equal budget compared to classical Random Search.
5. **Quantile Uncertainty Model (`QuantileUncertaintyPredictor`)**: Multi-quantile pinball loss regression estimating $q_{05}, q_{50}, q_{95}$ with guaranteed monotonic non-crossing post-processing.

---

## 3. Dataset Status
- **Validation Dataset**: Controlled synthetic maritime telemetry (`data/synthetic/synthetic_vessel_telemetry.csv`, 1,203 raw observations across 3 vessels: `VESSEL_FE_01`, `VESSEL_FE_02`, `VESSEL_HM_03`).
- **Clean Partition**: 1,190 valid records utilized after automated schema auditing and velocity consistency checks.
- **Dataset Identification**: Tagged with `DS-SYNTH-2026-01` and classified strictly as `SYNTHETIC_TEST_DATA` under `data/dataset_cards/synthetic_benchmark_dataset.yaml`.
- **Controlled Model Mismatch**: Generated synthetic data incorporates non-linear SFC bathtub variations, engine efficiency variance, and wave-wind interaction coupling ($F_{\text{synth}} = F_{\text{phys\_ref}} + \Delta F_{\text{mismatch}} + \epsilon_{\text{noise}}$) to eliminate circular evaluation.

---

## 4. Data Split Methodology & Leave-Vessel-Out Protocol
- **Temporal Splitting (Chronological)**:
  - **TRAIN**: First 70% of chronological observations ($N = 833$).
  - **VALIDATION**: Middle 15% of chronological observations ($N = 178$). Used exclusively for early stopping, $\alpha$-tuning, and QPSO/Random Search optimization.
  - **TEST**: Final 15% forward temporal horizon ($N = 179$). Touched only for final unbiased evaluation.
- **Leave-Vessel-Out Validation Protocol (Phase 2.1 Hardened)**:
  - For every held-out vessel, the remaining vessels are strictly partitioned into an inner **TRAIN (80%)** and **VALIDATION (20%)** split.
  - The held-out vessel serves as **TEST ONLY** and is never touched during:
    - Preprocessing fitting
    - Tree structure learning
    - Hyperparameter tuning
    - $\alpha$ residual weight selection
    - QPSO objective evaluation
  - Partition counts across folds:
    - **Fold 1 (`VESSEL_FE_01` Held Out)**: Inner Train = **638 rows**, Inner Validation = **160 rows**, Held-Out Test = **392 rows**.
    - **Fold 2 (`VESSEL_FE_02` Held Out)**: Inner Train = **634 rows**, Inner Validation = **159 rows**, Held-Out Test = **399 rows**.
    - **Fold 3 (`VESSEL_HM_03` Held Out)**: Inner Train = **634 rows**, Inner Validation = **159 rows**, Held-Out Test = **399 rows**.
- **Zero-Leakage Enforcement**: Categorical encodings, missing value imputations, and tree structures are fitted strictly on `TRAIN`.

---

## 5. Physics Model
- **Primary Hydrodynamic Speed**: Locked strictly to `stw_kn` (Speed Through Water). Silent substitution with `sog_kn` is forbidden and enforced via input validation.
- **SOG / STW / Current Consistency**:
  - SOG and STW are converted from knots to SI units: $STW_{\text{ms}} = STW_{\text{kn}} \times 0.514444$, $SOG_{\text{ms}} = SOG_{\text{kn}} \times 0.514444$.
  - 2D vector triangle closure: $\vec{V}_{\text{ground}} = \vec{V}_{\text{water}} + \vec{V}_{\text{current}}$.
  - Magnitude screening heuristic: $|SOG_{\text{ms}} - STW_{\text{ms}}| \le current\_speed\_ms + \text{tolerance}$.
  - Limitation: Without vessel heading and drift angle, exact vector triangle closure cannot be computed; magnitude checks serve solely as a screening heuristic.
- **Test Performance**:
  - **MAE**: 453.89 kg/h | **RMSE**: 514.45 kg/h | **MAPE**: 135.36% | **$R^2$**: -38.77

---

## 6. Physics Error Decomposition (EXP-PHYS-DECOMP-01)
Detailed investigation into why Physics MAE (453.89 kg/h) is dramatically worse than ML MAE (5.61 kg/h), documented in `results/experiments/physics_error_decomposition.md` and `results/experiments/physics_error_decomposition.csv`:

| Discrepancy Component | Mean Offset | Share of Error | Root Cause Mechanism |
| :--- | :--- | :--- | :--- |
| **Holtrop-Mennen Wetted Surface Drag Offset** | **+264.4 kg/h** | **58.2%** | Uncalibrated naval architecture coefficients overestimate mean brake power by +1,500 kW relative to synthetic ground truth. |
| **Auxiliary Hotel & Boiler Ingestion Mismatch** | **+174.5 kg/h** | **38.4%** | `physics/propulsion.py` includes a 450 kW auxiliary generator (94.5 kg/h) + 80 kg/h boiler. The synthetic generator models main engine propulsion telemetry only. |
| **SFC Bathtub Curve Parameterization** | **~15.0 kg/h** | **3.4%** | Discrepancy between ISO 3046 standard curves and specific synthetic engine tuning. |
| **Total Error** | **+453.89 kg/h** | **100.0%** | Systematic positive physical overprediction. |

> [!NOTE]
> In accordance with Phase 2.1 instructions, the physics model was **NOT modified** simply to improve its score. This is an objective audit of model discrepancy, not post-hoc parameter fitting.

---

## 7. ML Model Performance
- **Algorithm**: LightGBM regressor with Huber/L1 loss robustness.
- **Preprocessing**: Raw canonical numerical features used directly (no `StandardScaler`).
- **Feature Set**: `CONFIG-A` (operational/environmental features excluding `vessel_id`).
- **Test Performance**:
  - **MAE**: **5.61 kg/h**
  - **RMSE**: **9.60 kg/h**
  - **MAPE**: **1.54%**
  - **$R^2$**: **0.9862**
  - **Mean Bias**: -0.55 kg/h | **Median Abs Error**: 3.96 kg/h | **Max Abs Error**: 78.94 kg/h

---

## 8. Residual Hybrid Model Performance
- **Formulation**: $\hat{F} = \max(0, F_{\text{phys}} + \alpha \cdot \hat{r})$ where $r_i = F_{\text{obs}, i} - F_{\text{phys}, i}$.
- **Alpha Selection**: Evaluated on validation loss. Optimal $\alpha = 1.00$.
- **Test Performance**:
  - **MAE**: **21.40 kg/h**
  - **RMSE**: **30.73 kg/h**
  - **MAPE**: **6.25%**
  - **$R^2$**: **0.8581**

---

## 9. Multi-Seed QPSO vs. Random Search Benchmark
To establish statistical reproducibility under matched conditions, QPSO and Random Search were evaluated across **10 independent matched seeds** (`42, 101, 202, 303, 404, 505, 606, 707, 808, 909`) with an **identical evaluation budget of 225 objective evaluations** per seed (`results/experiments/qpso_random_multiseed.csv` and `results/experiments/qpso_random_statistics.json`):

### Aggregate Performance Summary (10 Seeds, Budget = 225)

| Metric | QPSO Mean $\pm$ SD | QPSO Median | Random Search Mean $\pm$ SD | Random Search Median | Paired Diff (QPSO - RS) | 95% CI of Difference |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Validation MAE (kg/h)** | **20.86 $\pm$ 0.76** | **20.63** | 24.74 $\pm$ 1.57 | 24.39 | **-3.88 $\pm$ 1.88** | **[-5.22, -2.54]** |
| **Final Test MAE (kg/h)** | **22.42 $\pm$ 1.40** | **22.17** | 23.48 $\pm$ 1.80 | 23.64 | **-1.06 $\pm$ 2.36** | **[-2.75, +0.63]** |
| **Runtime (s)** | 21.56 $\pm$ 10.92 | 21.01 | 17.55 $\pm$ 8.80 | 15.46 | +4.01 $\pm$ 4.70 | [+0.65, +7.37] |

### Statistical Hypothesis Testing (Paired Wilcoxon Signed-Rank Test)

1. **Validation MAE (Optimization Objective)**:
   - **Wilcoxon Statistic**: $W = 0.0$
   - **$p$-value**: **$0.00195$** ($p < 0.01$)
   - **Effect Size (Cohen's $d$)**: **$-2.06$** (Very Large Effect)
   - **Finding**: QPSO consistently and statistically significantly achieves lower validation loss than Random Search under matched budgets on the optimization objective.
2. **Final Test MAE (Generalization Error)**:
   - **Wilcoxon Statistic**: $W = 14.0$
   - **$p$-value**: **$0.1934$** ($p > 0.05$, Not Statistically Significant)
   - **Effect Size (Cohen's $d$)**: **$-0.45$** (Moderate Effect)
   - **Finding**: Although QPSO achieved lower mean test MAE (22.42 vs 23.48 kg/h), the difference is **not statistically significant** across 10 matched seeds at the $\alpha = 0.05$ level.
3. **Single-Seed vs. Aggregate Claim Correction**:
   - *Single-Seed Fact*: "Under seed 42 and an equal 225-evaluation budget, QPSO achieved 7.1% lower validation MAE than Random Search."
   - *Multi-Seed Aggregate Finding*: "Across 10 independent matched seeds with 225 evaluations, QPSO demonstrated a statistically significant advantage on the validation objective ($p = 0.0020$), but generalization differences on the test set were not statistically significant ($p = 0.1934$)."
   - *Epistemic Lock*: QPSO is a **classical quantum-behaved metaheuristic**. Claims of "quantum supremacy", "quantum advantage", or "quantum speedup" are rejected.

---

## 10. Quantile Uncertainty Calibration
Multi-quantile pinball regression evaluated on the chronological test partition ($N_{\text{test}} = 179$):
- **Prediction Interval Nominal Coverage**: 90% target interval ($q_{05} \to q_{95}$).
- **Empirical Coverage (PICP)**: **87.15%** (156 / 179 observations within bounds).
- **Coverage Error**: **-2.85%** relative to nominal 90% prediction interval.
- **Wilson Score 95% Confidence Interval for PICP**: **[81.42%, 91.33%]**.
  - The empirical coverage rate of 87.15% is cleanly bounded within the 95% confidence interval, indicating reliable interval calibration given sample size $N = 179$.
- **Mean Prediction Interval Width (MPIW)**: **56.35 kg/h** (11.43% of target range).
- **Mean Pinball Loss**: **2.50 kg/h**.
- **Monotonicity**: Post-processing guarantees $q_{05} \le q_{50} \le q_{95}$ with zero quantile crossing.
- **Terminology Adherence**: Evaluated intervals are designated strictly as **prediction intervals**, never as confidence intervals.

---

## 11. Temporal Stability Evaluation (EXP-PRED-05)
Chronological stability evaluated by dividing the forward test horizon into earlier and later intervals:
- **Early Test MAE**: 20.85 kg/h
- **Late Test MAE**: 21.38 kg/h
- **Absolute Difference**: **+0.53 kg/h** (Late - Early)
- **Relative Change**: **+2.54%**
- **Interpretation**: "Performance changed by +2.5% between the evaluated early and late portions of the test horizon." This reflects minimal temporal drift under stationary synthetic simulation, but multi-month operational wear remains unmodeled.

---

## 12. Cross-Vessel Evaluation (EXP-PRED-06)
Leave-vessel-out evaluation performed using **CONFIG-A (strictly excluding `vessel_id`)** with inner validation isolation:

| Holdout Vessel | Vessel Type | Training Rows | Validation Rows | Held-Out Test Rows | Physics MAE (kg/h) | ML MAE (kg/h) | Hybrid MAE (kg/h) | Best Model |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- | :--- |
| **VESSEL_FE_01** | Container Feeder | 638 | 160 | 392 | 301.85 | **7.67** | 24.56 | **ML-Only** |
| **VESSEL_FE_02** | Container Feeder | 634 | 159 | 399 | 288.99 | **8.83** | 27.52 | **ML-Only** |
| **VESSEL_HM_03** | Bulk Handymax | 634 | 159 | 399 | 755.52 | **121.35** | 478.72 | **ML-Only** |

- **Sister-Vessel Transfer**: Accurate transfer between sister feeder vessels (`VESSEL_FE_01` $\leftrightarrow$ `VESSEL_FE_02`) with MAE $7.67 - 8.83\,\text{kg/h}$.
- **Cross-Class Domain Shift**: Transferring to an unseen vessel class (Handymax Bulk Carrier) without bulk training data causes error to rise to **121.35 kg/h for ML** and **478.72 kg/h for Hybrid**.
- **Interpretation**: "Under this synthetic cross-vessel / domain-shift benchmark, models trained exclusively on container feeder vessels exhibit significant error degradation when applied to an unobserved bulk carrier class." This is not generalized as a universal real-world maritime failure.

---

## 13. Ablation Study & Feature Sensitivity (EXP-PRED-07)
Systematic ablation of information sources recorded in `results/experiments/ablation_study.csv`:

| Ablation Category | Variant | Test MAE (kg/h) | Test RMSE (kg/h) | Test $R^2$ |
| :--- | :--- | :--- | :--- | :--- |
| **Model Family** | A. ML-Only (CONFIG-A) | **5.61** | **9.60** | **0.9862** |
| **Model Family** | B. ML-Only (No Metocean Environment) | 5.62 | 9.41 | 0.9867 |
| **Model Family** | C. Physics + ML Residual (alpha tuned) | 21.40 | 30.73 | 0.8581 |
| **Model Family** | D. Physics + ML Residual + QPSO | 21.12 | 29.69 | 0.8676 |
| **Feature Ablation** | Without Wind | 5.68 | 9.46 | 0.9866 |
| **Feature Ablation** | Without Waves | 5.74 | 9.50 | 0.9864 |
| **Feature Ablation** | Without Current | 5.61 | 9.45 | 0.9866 |
| **Feature Ablation** | Without Draft/Displacement | 5.48 | 9.45 | 0.9866 |
| **Feature Ablation** | Without RPM | 5.67 | 9.55 | 0.9863 |
| **Feature Ablation** | **Without Shaft Power** | **7.92** | **11.70** | **0.9794** |
| **Vessel ID** | CONFIG-B (Including vessel_id) | 5.68 | 9.40 | 0.9867 |

### Hardened Ablation Insights:
1. **Shaft Power Sensitivity**: Under the evaluated synthetic benchmark, shaft power was the **most performance-sensitive feature among the tested ablations** (dropping shaft power increased MAE from 5.61 to 7.92 kg/h, +41.2% error).
2. **Metocean Variables**: Removing wind/wave variables produced **small changes in predictive error under the evaluated benchmark** (+0.07 kg/h without wind, +0.13 kg/h without waves). Statistical significance is not asserted for environmental ablations without repeated-seed testing.
3. **Vessel ID Invariance**: Omitting `vessel_id` in CONFIG-A preserved predictive accuracy (5.61 kg/h vs 5.68 kg/h) while ensuring robust sister-vessel transfer.

---

## 14. Synthetic Target Dependency Audit
Documented in `results/experiments/synthetic_target_dependency.md`:
- In `data/synthetic_generator.py`, the target `fuel_mass_flow_kg_h` is computed as:
  $$F_t = \frac{\text{shaft\_power\_kw} \cdot \text{SFC}(\text{load\_frac})}{1000.0} + \epsilon_{\text{meas}}$$
  where $\text{shaft\_power\_kw} \equiv P_{\text{brake}}$ is generated from calm-water, wave, and aerodynamic drag formulas, and $\text{load\_frac} = \text{shaft\_power\_kw} / P_{\text{max}}$.
- **Mathematically Upstream Features**: `shaft_power_kw`, `engine_load_pct`, `stw_kn`, `wave_height_m`, `wind_speed_ms`, and `draft_m`.
- **Methodological Implication**: Because `shaft_power_kw` is physically upstream of `fuel_mass_flow_kg_h` at the same time $t$, this benchmark represents **synchronous operational estimation**, NOT future forecasting. This is an intrinsic characteristic of operational telemetry, not data leakage.

---

## 15. Leakage & Integrity Audit
- **Temporal Monotonicity**: Strictly monotonic split; no test observation occurred prior to training or validation timestamps.
- **Held-Out Vessel Isolation**: Zero overlap across train, validation, and held-out test sets. The test vessel was never passed to tuning or selection.
- **Preprocessing Isolation**: Categorical dtypes and missing-value statistics fitted strictly on `TRAIN`.
- **Git Commit Tracking**: Commit hash `3a6d4e2b50e59740c933d86cfda7ba0779b2d485` verified and recorded across all generated experiment artifacts.

---

## 16. Scientific Findings
1. **Empirical Model Ranking**: Under controlled synthetic evaluation with model mismatch:
   $$\text{ML-Only (LightGBM)} \succ \text{Physics+ML Residual (QPSO)} \succ \text{Physics+ML Residual (Base)} \succ \text{Physics-Only}$$
2. **Feature Sensitivity**: Shaft power is the most performance-sensitive predictor of instantaneous fuel rate under this synthetic benchmark.
3. **QPSO Search Utility**: Classical QPSO proved statistically superior to Random Search on the validation optimization objective ($p = 0.0020$), while test MAE differences remained statistically non-significant ($p = 0.1934$).

---

## 17. Negative Findings (Preserved)
1. **Refutation of Universal Hybrid Superiority**: The hypothesis that a physics-informed residual model would outperform pure ML is **REFUTED on this benchmark dataset** (ML MAE 5.61 kg/h vs Hybrid MAE 21.12 kg/h). Uncalibrated theoretical drag acted as a source of structural bias.
   > *"The physics-informed residual hypothesis was not supported by this synthetic benchmark."*
2. **Cross-Class Domain Shift**: Models trained on container feeders cannot predict bulk carriers without retraining (MAE rose to 121.35 kg/h).
3. **No Quantum Advantage**: QPSO operates as a classical stochastic search; it offers no quantum speedup or exponential scaling.

---

## 18. Limitations
1. **Synthetic Data Dependency**: All experiments were conducted on `SYNTHETIC_TEST_DATA`. Results cannot be cited as real-world maritime operational accuracy.
2. **Velocity Vector Closure Heuristic**: Without directional velocity information (heading and drift angle), magnitude checks serve strictly as a screening heuristic.
3. **Naval Architecture Drag Curves**: Default resistance coefficients were not calibrated with towing-tank sea-trial data for specific hulls.
4. **Absence of Multi-Year Degradation**: Long-term biofouling and propeller wear dynamics are not represented in the short-horizon synthetic series.

---

## 19. Final Recommendation
**STATUS: FREEZE PHASE 2 / FURTHER AUDIT REQUIRED**  
**DO NOT START PHASE 3.**
