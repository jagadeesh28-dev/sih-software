# PHASE 6: FROZEN BASELINE CERTIFICATE & AUDIT
## SIH26138 — Egreen Quanta
**Audit Date:** 2026-09-19  
**Status:** `CONFIRMED & FROZEN`  
**Execution Environment:** Windows 11 AMD64, Python 3.14.0, LightGBM 4.7.0, NumPy 2.2.6, SciPy 1.17.0, Pandas 2.3.0  
**Verification Script:** [`scripts/phase6_baseline_reproduce.py`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/scripts/phase6_baseline_reproduce.py)  

---

### 1. Telemetry Dataset Provenance & Record Count

The evaluation is conducted on the validated, real-world maritime telemetry repository from the FuelCast dataset:

| Vessel Identifier | Vessel Class | Displacement | Total Records | Split Ratio | Train Rows (60%) | Val Rows (20%) | Test Rows (20%) |
|---|---|---|---|---|---|---|---|
| **`CPS_Poseidon`** | Container Feeder | 24,000 t | 105,422 | Chronological | 63,253 | 21,084 | 21,085 |
| **`CPS_Triton`** | Container Feeder | 24,000 t | 25,347 | Chronological | 15,208 | 5,069 | 5,070 |
| **`OSS_Ceto`** | Bulk Handymax | 45,000 t | 43,205 | Chronological | 25,923 | 8,641 | 8,641 |
| **FLEET TOTAL** | **Combined** | — | **173,974** | **Chronological** | **104,384** | **34,794** | **34,796** |

- **Target Variable:** `fuel_mass_flow_kg_h` (Continuous positive mass flow rate, $\text{kg/h}$).
- **Target Nulls / NaNs:** 0 (Strictly zero missing target values).
- **Physical Bounds:** $\text{fuel\_mass\_flow\_kg\_h} \ge 0.0$ for all records.

---

### 2. Feature Policy (`CONFIG_REAL_A`)

To prevent memorization and guarantee cross-vessel generalization, `MODEL-REAL-04` utilizes strictly hydrodynamic, kinematic, and metocean features. Machinery internal sensors (shaft power, RPM, torque, and engine load percentage) are **excluded**:

| Feature Name | Category | Unit | Description |
|---|---|---|---|
| `stw_kn` | Kinematic (Hydrodynamic) | knots | Speed Through Water (mandatory primary speed) |
| `sog_kn` | Kinematic (Geodetic) | knots | Speed Over Ground |
| `draft_m` | Hydrostatic | meters | Vessel dynamic mean draft |
| `displacement_t` | Hydrostatic | metric tonnes | Submerged displacement mass |
| `wind_speed_ms` | Metocean | m/s | True wind speed |
| `wind_direction_deg` | Metocean | degrees | True wind direction relative to bow |
| `wave_height_m` | Metocean | meters | Significant wave height ($H_{s}$) |
| `wave_period_s` | Metocean | seconds | Peak wave period ($T_{p}$) |
| `wave_direction_deg` | Metocean | degrees | Relative wave heading |
| `current_speed_ms` | Metocean | m/s | Ocean current velocity |
| `current_direction_deg` | Metocean | degrees | Ocean current heading |
| `water_depth_m` | Hydrodynamic | meters | Under-keel water depth (shallow water effect) |
| `vessel_type` | Hull Class | categorical | Feeder container vs Handymax bulk carrier |
| `fuel_type` | Energy Source | categorical | HFO, MGO, or VLSFO grade |

---

### 3. Model Mathematical Specification

The frozen hybrid residual architecture is governed by:
$$\hat{y}(x) = \max\left(0, y_{\text{physics}}(x) + \alpha \cdot \hat{r}_{\text{ML}}(x)\right)$$

1. **Hydrodynamic Physics Model ($y_{\text{physics}}$):**
   - Calm water total resistance calculated via Holtrop-Mennen (1982, 1984) regression equations based on vessel hydrostatic coefficients.
   - Added resistance in irregular waves calculated using Kwon / STAwave-2 semi-empirical formulations.
   - Aerodynamic superstructure resistance calculated via Isherwood / Blendermann formulation.
   - Propulsion efficiency chain: Effective power $P_E \to$ Delivered power $P_D = P_E / \eta_D \to$ Brake power $P_B = P_D / \eta_S \to$ Specific Fuel Oil Consumption (SFOC) mapping to obtain mass flow ($\text{kg/h}$).
2. **Machine Learning Residual Regressor ($\hat{r}_{\text{ML}}$):**
   - LightGBM Gradient Boosted Decision Tree regressor trained strictly on training residuals:
     $$r_i = y_i - y_{\text{physics}}(x_i), \quad i \in \text{TRAIN}$$
   - Hyperparameters: `n_estimators=150`, `learning_rate=0.05`, `num_leaves=31`, `max_depth=6`, `min_child_samples=20`, `subsample=0.8`, `colsample_bytree=0.8`, `reg_alpha=0.1`, `reg_lambda=1.0`, `seed=42`.
3. **Coupling Coefficient ($\alpha$):**
   - Swept over grid $\{0.0, 0.25, 0.50, 0.75, 1.00\}$ evaluated strictly on the VALIDATION split.
   - Optimal value selected: $\alpha = 1.00$.

---

### 4. Verified Numerical Baseline (Chronological Test Set)

The exact independent execution of `scripts/phase6_baseline_reproduce.py` on 2026-09-19 confirmed:

| Metric | Target Frozen Value | Reproduced Measured Value | Absolute Difference | Verification Status |
|---|---|---|---|---|
| **$R^2$ Score** | **0.9501** | **0.9501** | **0.0000** | **`EXACT MATCH (PASS)`** |
| **MAE ($\text{kg/h}$)** | **246.97** | **246.97** | **0.00** | **`EXACT MATCH (PASS)`** |
| **RMSE ($\text{kg/h}$)** | **443.21** | **443.21** | **0.00** | **`EXACT MATCH (PASS)`** |
| **MAPE ($\%$)** | **14.63%** | **14.63%** | **0.00%** | **`EXACT MATCH (PASS)`** |
| **Median Absolute Error** | **129.31** | **129.31** | **0.00** | **`EXACT MATCH (PASS)`** |
| **Mean Bias ($\text{kg/h}$)** | **-141.82** | **-141.82** | **0.00** | **`EXACT MATCH (PASS)`** |
| **Physics-Only MAE** | **1,885.45** | **1,885.45** | **0.00** | **`EXACT MATCH (PASS)`** |
| **Physics-Only $R^2$** | **-0.5471** | **-0.5471** | **0.0000** | **`EXACT MATCH (PASS)`** |

---

### 5. Data Leakage Forensic Audit (10 Criteria)

1. **Timestamp Ordering:** Strict forward chronological ordering per vessel; zero future records in train.
2. **Vessel Leakage:** Each vessel's time series split independently into 60% train, 20% val, 20% test before concatenating into fleet partitions.
3. **Future-Feature Leakage:** No rolling features computed across test-to-train boundaries.
4. **Target Leakage:** Target `fuel_mass_flow_kg_h` excluded from input feature matrix $X$.
5. **Scaling Leakage:** Scalers and encoders fit strictly on `TRAIN`; unseen categories mapped to `NaN`.
6. **Imputation Leakage:** Imputation statistics computed strictly on `TRAIN`.
7. **Feature-Engineering Leakage:** Derived domain features computed per-row without cross-sample statistics.
8. **Window Overlap:** Zero overlapping temporal windows between train, val, and test.
9. **Hyperparameter Leakage:** Hyperparameters and $\alpha$ selected exclusively on `VALIDATION`; `TEST` is evaluated once.
10. **Cross-Vessel Leakage:** Categorical levels learned strictly on training partitions.

---

### 6. Baseline Freeze Declaration

This baseline is **FROZEN**. Under no circumstances may this baseline be silently adjusted or modified to make quantum-inspired methods appear superior. All Phase 6 candidate QI models will be benchmarked directly against this immutable standard.
