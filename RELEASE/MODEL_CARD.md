# Formal Model Cards: QI-C1 and MODEL-REAL-04
### SIH26138 — Egreen Quanta (v1.0.0)

This document specifies the intended usage, data lineage, performance boundaries, and failure modes for the two production fuel prediction engines in Egreen Quanta.

---

## 1. Model Card: Candidate QI-C1 (Primary Production Engine)

### 1.1 Model Details
- **Model Identifier:** `QI-C1`
- **Formal Name:** Quantum-Inspired Optimized Fuel Predictor
- **Version:** `1.0.0-production`
- **Architecture:** 8-Feature Subset selected via Quantum-Inspired Evolutionary Algorithm (QIEA) with Han & Kim rotation gates + LightGBM Regressor on physical residual ($r = y - F_{\text{phys}}$).
- **Coupling Equation:** $\hat{y} = \max(0, F_{\text{phys}}(STW) + 1.0 \cdot \hat{r}(X_{qi}))$
- **Checksum:** Text booster stored in `models/qi_c1.txt`.

### 1.2 Intended Use
- **Primary Domain:** Continuous operational fuel consumption prediction for commercial maritime vessels equipped with direct Coriolis mass-flow meters.
- **Decision Context:** Fleet dispatch speed scheduling, route weather optimization, and bunker compliance monitoring.

### 1.3 Out-of-Scope / Non-Intended Use
- **Uncalibrated Hulls:** Must not be deployed zero-shot to commercial vessel classes without prior historical telemetry calibration.
- **Inland Small Craft:** Not validated for high-speed planing craft, catamarans, or river barges.
- **Autonomous Throttle Control:** Intended strictly as a human-in-the-loop decision support advisor.

### 1.4 Training & Validation Data
- **Dataset:** DTU FuelCast Maritime Telemetry (604 vessel-days across 3 commercial hulls).
- **Split Scheme:** Forward chronological partition (60% train: 104,384 rows; 20% validation: 34,794 rows; 20% test: 34,796 rows).
- **Input Features (8 selected):** `stw_kn`, `sog_kn`, `draft_m`, `displacement_t`, `wind_speed_ms`, `wave_height_m`, `current_speed_ms`, `water_depth_m`.

### 1.5 Performance Metrics
- **Test $R^2$:** $0.9530 \pm 0.0012$ (across 30 seeds)
- **Test MAE:** $237.96 \pm 5.46\text{ kg/h}$
- **Test MAPE:** $14.18\%$
- **Inference Latency:** Mean $0.096\text{ ms}$ (P95: $0.203\text{ ms}$)

### 1.6 OOD Behavior & Safety Gate
- Supervised by `DomainChecker`. Queries with normalized envelope distance $>1.00$ trigger automatic fallback to `MODEL-REAL-04`; distance $>3.00$ triggers immediate execution halt and rejection.

---

## 2. Model Card: MODEL-REAL-04 (Reference / High-Reliability Fallback)

### 2.1 Model Details
- **Model Identifier:** `MODEL-REAL-04`
- **Formal Name:** Classical Hybrid Physics + ML Residual Predictor
- **Version:** `1.0.0-frozen`
- **Architecture:** Holtrop-Mennen calm water + IMO STAwave-2 added wave drag + Blendermann wind drag, coupled with a 14-feature LightGBM residual regressor.
- **Checksum:** Text booster stored in `models/model_real_04.txt`.

### 2.2 Operational Role
- Serves as the immutable reference anchor and high-reliability fallback engine during near-boundary extrapolation, high-uncertainty events, or primary booster failure.

### 2.3 Performance Metrics
- **Test $R^2$:** $0.9501$ (Seed 42); $0.9503$ in release verification.
- **Test MAE:** $246.97\text{ kg/h}$ (Seed 42 test); $248.12\text{ kg/h}$ (30-seed mean).
- **Test MAPE:** $14.63\%$
- **Test RMSE:** $443.21\text{ kg/h}$

---

## 3. Audited Negative Results (QI-C2 MPS)

- **Model Identifier:** `QI-C2-MPS` (Matrix Product State Tensor Network)
- **Status:** **REJECTED NEGATIVE RESULT (NOT IN PRODUCTION)**
- **Audit Findings:** Unconstrained continuous SGD optimization on tabular continuous maritime telemetry diverged across 20/30 random seeds ($\text{MAE} > 10^{11}\text{ kg/h}$). Retained in research archive as scientific evidence of the non-applicability of simple 1D lattice tensor trains to tabular telemetry.
