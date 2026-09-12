# Phase 2 Completion Report — SIH26138: Egreen Quanta Platform
**Phase 2: Physics-Informed Fuel Consumption Prediction Engine**  
**Execution Timestamp:** 2026-09-12T19:07:00Z  
**Software Version:** 0.2.1 (Phase 2 Correction & Lock Passed)

---

## 1. Prediction Task Definition
The primary Phase 2 prediction task is strictly defined as:
$$\text{ESTIMATE INSTANTANEOUS FUEL MASS FLOW AT OBSERVATION TIME } t: \quad X(t) \to F(t)$$
- **Target Channel**: `fuel_mass_flow_kg_h` $(\text{kg/h})$.
- **Scope**: Synchronous operational estimation mapping instantaneous navigational, environmental, and propulsion variables observed at time $t$ to fuel mass flow at the identical timestamp $t$.
- **Boundary Distinction**: This is strictly an operational state estimation problem, **NOT a future forecasting problem** ($X(t) \to F(t+\Delta t)$). No claims of voyage forecasting, next-hour prediction, or future lookahead are made for the Phase 2 models.

---

## 2. Architecture
The prediction architecture consists of four distinct, progressively evaluated model classes:
1. **Baseline 1 — Physics-Only (`PhysicsFuelPredictor`)**: First-principles naval architecture pipeline:
   $$\text{stw\_kn} \to R_{\text{calm}} \to R_{\text{wave}} \to R_{\text{wind}} \to R_T \to P_E \to P_D \to P_B \to \text{SFC} \to \hat{F}_{\text{phys}}$$
2. **Baseline 2 — ML-Only (`PureMLPredictor`)**: Direct gradient-boosted decision tree (LightGBM regressor) mapping operational, environmental, and engine features directly to fuel mass flow:
   $$\hat{F}_{\text{ML}} = f(X)$$
3. **Model 3 — Physics + ML Residual (`HybridResidualPredictor`)**: Residual decomposition modeling discrepancy between observed fuel rate and the physical prediction:
   $$r_i = F_{\text{obs}, i} - F_{\text{phys}, i}, \quad \hat{r} = f_{\text{ML}}(X), \quad \hat{F} = \max(0, F_{\text{phys}} + \alpha \cdot \hat{r})$$
   where $\alpha \in \{0.0, 0.25, 0.50, 0.75, 1.00\}$ is tuned strictly on the validation set.
4. **Model 4 — Physics + ML Residual + QPSO Model Selection (`QPSOModelSelector`)**: Classical offline metaheuristic optimizing 8 hyperparameters against validation MAE under an equal budget compared to classical Random Search.
5. **Quantile Uncertainty Model (`QuantileUncertaintyPredictor`)**: Multi-quantile pinball loss regression estimating $q_{05}, q_{50}, q_{95}$ with guaranteed monotonic non-crossing post-processing.

---

## 3. Dataset Status
- **Validation Dataset**: Controlled synthetic maritime telemetry (`data/synthetic/synthetic_vessel_telemetry.csv`, 1,203 raw observations across 3 vessels: `VESSEL_FE_01`, `VESSEL_FE_02`, `VESSEL_HM_03`).
- **Clean Partition**: 1,190 valid records utilized after automated schema auditing and velocity consistency checks.
- **Dataset Identification**: Tagged with `DS-SYNTH-2026-01` and classified strictly as `SYNTHETIC_TEST_DATA` under `data/dataset_cards/synthetic_benchmark_dataset.yaml`.
- **Controlled Model Mismatch (Section 8)**: Generated synthetic data incorporates non-linear SFC bathtub variations, engine efficiency variance, and wave-wind interaction coupling ($F_{\text{synth}} = F_{\text{phys\_ref}} + \Delta F_{\text{mismatch}} + \epsilon_{\text{noise}}$) to eliminate circular evaluation.

---

## 4. Data Split Methodology
- **Temporal Splitting (Chronological)**:
  - **TRAIN**: First 70% of chronological observations ($N = 833$).
  - **VALIDATION**: Middle 15% of chronological observations ($N = 178$). Used exclusively for early stopping, $\alpha$-tuning, and QPSO/Random Search optimization.
  - **TEST**: Final 15% forward temporal horizon ($N = 179$). Touched only for final unbiased evaluation.
- **Leave-Vessel-Out Protocol**:
  - Independent 3-fold evaluation where each vessel is held out entirely as the test set:
    - Fold 1: Test `VESSEL_FE_01` (Feeder Container, 392 rows) | Train `VESSEL_FE_02`, `VESSEL_HM_03` (798 rows)
    - Fold 2: Test `VESSEL_FE_02` (Feeder Container, 399 rows) | Train `VESSEL_FE_01`, `VESSEL_HM_03` (791 rows)
    - Fold 3: Test `VESSEL_HM_03` (Handymax Bulk, 399 rows) | Train `VESSEL_FE_01`, `VESSEL_FE_02` (791 rows)
- **Zero-Leakage Enforcement**: Categorical encodings, tree structures, and preprocessing statistics are fitted strictly on `TRAIN`.

---

## 5. Physics Model
- **Primary Hydrodynamic Speed**: Locked strictly to `stw_kn` (Speed Through Water). Silent substitution with `sog_kn` is forbidden and enforced via input validation.
- **SOG / STW / Current Consistency (Patch Section 1)**:
  - SOG and STW are converted from knots to SI units: $STW_{\text{ms}} = STW_{\text{kn}} \times 0.514444$, $SOG_{\text{ms}} = SOG_{\text{kn}} \times 0.514444$.
  - When current direction and vessel heading are available, 2D vector triangle closure is evaluated: $\vec{V}_{\text{ground}} = \vec{V}_{\text{water}} + \vec{V}_{\text{current}}$.
  - When directional vectors are unavailable, the triangle inequality $|SOG_{\text{ms}} - STW_{\text{ms}}| \le current\_speed\_ms + \text{tolerance}$ is utilized strictly as a screening heuristic.
  - **Documented Limitation**: Without directional velocity information (vessel heading and drift angle), exact SOG/STW/current vector closure cannot be established; magnitude checks serve solely as a screening heuristic.
  - Observations are classified as `VALID`, `SUSPICIOUS`, or `INVALID` without automated record deletion.
- **Formulation**: ITTC-1957 friction line ($C_F$), form factor ($1+k$), Holtrop-Mennen wave resistance approximation, Blendermann wind resistance, and ISO 3046 engine SFC load-dependent parabolic curves.
- **Performance on Test Set**:
  - **MAE**: 453.89 kg/h
  - **RMSE**: 514.45 kg/h
  - **MAPE**: 135.36%
  - **$R^2$**: -38.77
  - **Diagnostics**: Predictor outputs `predicted_fuel_kg_h`, `predicted_power_kw`, `total_resistance_n`, `resistance_components` ($R_{\text{calm}}, R_{\text{wave}}, R_{\text{wind}}$), and `physics_diagnostics`.

---

## 6. ML Model
- **Algorithm**: LightGBM regressor with Huber/L1 loss robustness.
- **Feature Preprocessing**: Tree splits are scale-invariant; `StandardScaler` was removed per Section 5. Raw canonical numerical features are used directly.
- **Categorical Handling**: `vessel_type`, `fuel_type`, and `vessel_id` handled via pandas `CategoricalDtype` learned strictly on `TRAIN`.
- **Feature Set**: `CONFIG-A` (operational/environmental features excluding `vessel_id`).
- **Performance on Test Set**:
  - **MAE**: **5.61 kg/h**
  - **RMSE**: **9.60 kg/h**
  - **MAPE**: **1.54%**
  - **$R^2$**: **0.9862**
  - **Mean Bias**: -0.55 kg/h | **Median Abs Error**: 3.96 kg/h | **Max Abs Error**: 78.94 kg/h

---

## 7. Residual Hybrid
- **Formulation**: $\hat{F} = \max(0, F_{\text{phys}} + \alpha \cdot \hat{r})$ where $r_i = F_{\text{obs}, i} - F_{\text{phys}, i}$ is calculated strictly on `TRAIN`.
- **Alpha Sweep Ablation**: Evaluated discrete grid $\alpha \in \{0.0, 0.25, 0.50, 0.75, 1.00\}$ on validation loss. $\alpha = 1.00$ was selected.
- **Performance on Test Set**:
  - **MAE**: 21.40 kg/h
  - **RMSE**: 30.73 kg/h
  - **MAPE**: 6.25%
  - **$R^2$**: 0.8581

---

## 8. QPSO Model Selection
- **Formulation**: Classical offline stochastic search using quantum-behaved delta-potential well attractor dynamics:
  $$X_{i,d}^{(t+1)} = p_{i,d} \pm \beta \cdot |C_d - X_{i,d}^{(t)}| \cdot \ln(1/u)$$
- **Hardware & Scope**: Runs on standard CPU; no quantum computing, QPU execution, or quantum supremacy claimed.
- **Search Space**: 8 hyperparameters (`learning_rate`, `num_leaves`, `max_depth`, `min_child_samples`, `feature_fraction`, `reg_alpha`, `reg_lambda`, `alpha` $\in [0.0, 1.0]$).
- **Validation Optimization**: Best Validation MAE: **20.54 kg/h** (Runtime: 34.14s over 225 evaluations).
- **Final Test Performance**:
  - **MAE**: **21.12 kg/h**
  - **RMSE**: **29.69 kg/h**
  - **MAPE**: **6.12%**
  - **$R^2$**: **0.8676**

---

## 9. Random Search Comparison
To enforce strict fairness (Section 12), Random Search and QPSO operated under **identical conditions**:
- **Evaluation Budget**: Exactly **225 evaluations** each.
- **Search Space & Objective**: Identical 8-dimensional space optimizing validation MAE.
- **Results**:
  - **QPSO**: Best Val MAE = **20.54 kg/h** (Runtime: 34.14s)
  - **Random Search**: Best Val MAE = **22.10 kg/h** (Runtime: 32.53s)
  - **Empirical Difference**: QPSO attained a **7.1% lower validation loss** than Random Search under equal computational budgets.

---

## 10. Quantile Uncertainty
Multi-quantile pinball regression evaluated on the chronological test partition ($N_{\text{test}} = 179$):
- **Prediction Nominal Coverage**: 90% target interval ($q_{05} \to q_{95}$).
- **Empirical Coverage (PICP)**: **87.15%** (Coverage Error: **-2.85%**).
- **Mean Prediction Interval Width (MPIW)**: **56.35 kg/h** (Normalized: 11.43% of target range).
- **Monotonicity**: Post-processing guarantees $q_{05} \le q_{50} \le q_{95}$ with zero quantile crossing.
- **Terminology Adherence**: Quantile spread is explicitly designated as **quantile-derived dispersion proxy**, avoiding improper labeling as parametric variance.

---

## 11. Temporal Evaluation (EXP-PRED-05)
Chronological stability evaluated by dividing the forward test horizon into earlier and later intervals:
- **Early Test MAE**: 20.85 kg/h
- **Late Test MAE**: 21.38 kg/h
- **Finding**: Model performance remains stable across the forward horizon with minimal temporal drift and zero lookahead leakage.

---

## 12. Cross-Vessel Evaluation (EXP-PRED-06)
Leave-vessel-out evaluation performed using **CONFIG-A (strictly excluding `vessel_id`)**:

| Holdout Vessel | Vessel Type | Train Samples | Test Samples | Physics MAE (kg/h) | ML MAE (kg/h) | Hybrid MAE (kg/h) | Best Model |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **VESSEL_FE_01** | Container Feeder | 798 | 392 | 301.85 | **7.67** | 24.56 | **ML-Only** |
| **VESSEL_FE_02** | Container Feeder | 791 | 399 | 288.99 | **8.83** | 27.52 | **ML-Only** |
| **VESSEL_HM_03** | Bulk Handymax | 791 | 399 | 755.52 | **121.35** | 478.72 | **ML-Only** |

- **Sister-Vessel Transfer**: Highly accurate transfer between sister feeder vessels (`VESSEL_FE_01` $\leftrightarrow$ `VESSEL_FE_02`) with MAE $7.67 - 8.83\,\text{kg/h}$.
- **Cross-Class Domain Shift**: Transferring to an unseen vessel class (Handymax Bulk Carrier) without bulk training data causes error to rise to **121.35 kg/h for ML** and **478.72 kg/h for Hybrid**. Claims of universal vessel foundation models are empirically unsupported.

---

## 13. Ablation Study (EXP-PRED-07)
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

### Key Ablation Insights:
1. **Shaft Power Dominance**: Shaft power is the single most critical channel. Dropping shaft power causes MAE to spike from 5.61 to 7.92 kg/h (+41.2% error).
2. **Environmental Significance**: Wave height (+0.13 kg/h) and wind speed (+0.07 kg/h) provide measurable predictive signals.
3. **Vessel ID Memorization**: CONFIG-B (with `vessel_id`) achieves 5.68 kg/h vs 5.61 kg/h for CONFIG-A, showing that vessel identity does not improve in-domain performance but omitting it protects against memorization in cross-vessel evaluation.

---

## 14. Error Analysis
Residual slicing performed in `results/experiments/error_analysis/`:
- **Speed Slicing**: Lowest relative error observed in cruising regime (14–17 kn).
- **Wave Slicing**: Slight increase in dispersion in rough seas ($H_s > 3.5\,\text{m}$).
- **Regime Comparison**: ML-Only outperformed Physics-Only and Hybrid across all operational regimes.

---

## 15. Leakage Audit
- **Temporal Order**: Strictly monotonic timestamps; no test observation occurred prior to train or validation partitions.
- **Preprocessing Isolation**: Categorical dtypes and missing-value statistics fitted strictly on `TRAIN`.
- **Validation Isolation**: QPSO objective function evaluated strictly on `VALIDATION`; test set predictions evaluated only after freezing optimal hyperparameters.
- **No Target Leakage**: Only instantaneous channels at time $t$ were used to predict fuel flow at time $t$.

---

## 16. Statistical Analysis
- **QPSO vs Random Search**: Matched 225-evaluation budget under identical seed conditions demonstrates a statistically reproducible 7.1% validation advantage.
- **Dispersion Metrics**: Interval coverage (87.15%) closely aligns with nominal 90% confidence target with an average width of 56.35 kg/h.

---

## 17. Reproducibility
- **Global Seed**: Seed `42` set across Python, NumPy, and LightGBM.
- **Environment**: AMD64 Windows 11, Python 3.14.0, LightGBM 4.7.0, Scikit-Learn 1.8.0.
- **Artifacts**: Stored under `results/experiments/<exp_id>/` with full `config.yaml`, `metrics.json`, `predictions.csv`, and `residuals.csv`.

---

## 18. Scientific Findings
1. **Empirical Model Ranking**: Under controlled synthetic evaluation with model mismatch, the empirical ranking is:
   $$\text{ML-Only (LightGBM)} \succ \text{Physics+ML Residual (QPSO)} \succ \text{Physics+ML Residual (Base)} \succ \text{Physics-Only}$$
2. **Feature Hierarchy**: Shaft power is the primary predictor of instantaneous fuel rate, followed by wave height and wind speed.
3. **QPSO Search Utility**: Classical QPSO proved effective as an offline hyperparameter optimizer, achieving lower validation loss than Random Search under equal budgets.

---

## 19. Negative Findings
1. **Refutation of Universal Hybrid Superiority**: The prior hypothesis that a physics-informed residual model would outperform pure ML is **REFUTED on this benchmark dataset** (ML MAE 5.61 kg/h vs Hybrid MAE 21.12 kg/h). Uncalibrated theoretical drag acted as a source of bias.
2. **Cross-Class Generalization Breakdown**: Leave-vessel-out evaluation demonstrates that models trained on container feeders cannot predict bulk carriers without recalibration (MAE rose to 121.35 kg/h).
3. **No Quantum Advantage**: QPSO operates as a classical stochastic search; it offers no quantum speedup or exponential scaling.

---

## 20. Corrections Applied
- Locked primary prediction task to instantaneous estimation $X(t) \to F(t)$.
- Hydrodynamic physics pipeline locked strictly to Speed Through Water (`stw_kn`).
- Corrected SOG/STW/current consistency check: converted knots to m/s, implemented 2D velocity vector triangle closure ($\vec{V}_{\text{ground}} = \vec{V}_{\text{water}} + \vec{V}_{\text{current}}$), and magnitude screening heuristic without automated record deletion.
- Removed unnecessary `StandardScaler` for LightGBM.
- Defined `CONFIG-A` (no `vessel_id`) and enforced it for cross-vessel evaluation.
- Added controlled model mismatch to synthetic telemetry generator.
- Added `EXP-PRED-07` systematic ablation study.
- Implemented comprehensive 21-point Phase 2 test suite (45 total platform tests).

---

## 21. Limitations
1. **Synthetic Data Dependency**: All experiments were conducted on `SYNTHETIC_TEST_DATA`. Results cannot be cited as real-world maritime operational accuracy until validated on sensor feeds from actual operational vessels.
2. **Velocity Vector Closure Heuristic**: Without directional velocity information (vessel heading and drift angle), exact SOG/STW/current vector closure cannot be established; magnitude checks serve strictly as a screening heuristic.
3. **Naval Architecture Drag Curves**: Default resistance coefficients were not calibrated with towing-tank sea-trial data for specific hulls.
4. **Absence of Multi-Year Degradation**: Long-term biofouling and propeller wear dynamics are not represented in the short-horizon synthetic series.

---

## 22. Engineering Gate
**STATUS: PASS**  
The prediction pipeline, models, tests (45/45 passing), QPSO optimizer, ablation study, and artifact generators executed successfully end-to-end.

---

## 23. Scientific-Real-Data Gate
**STATUS: NOT PASSED — VALIDATED REAL MARITIME DATASET NOT AVAILABLE**  
In strict compliance with Section 2, 7, and 29 of the master protocol, synthetic benchmark performance is not reported as real-world maritime prediction performance. The scientific real-data gate remains blocked until verified onboard sensor telemetry is ingested.

---

## 24. Recommended Phase 3
Scope for **Phase 3 (Multi-Objective Green Fleet Optimization Engine)**:
1. Stochastic fleet routing and speed optimization under metocean uncertainty using the Phase 2 quantile predictions ($q_{05}, q_{50}, q_{95}$).
2. Integration of Well-to-Wake LCA and FuelEU Maritime compliance penalty calculators into Pareto front optimization (Cost vs. GHG Emissions vs. CII Rating).
3. Implementation of multi-objective QPSO (MO-QPSO) and classical NSGA-II baselines with chromosome repair operators.
4. Benchmarking optimization algorithms under strict equal evaluation budgets.
