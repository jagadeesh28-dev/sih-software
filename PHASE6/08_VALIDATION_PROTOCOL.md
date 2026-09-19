# PHASE 6 — STEP 8: COMPREHENSIVE VALIDATION PROTOCOL
## SIH26138 — Egreen Quanta
### Temporal Splitting, Rolling-Origin, Leave-One-Vessel-Out (LOVO), Regimes, and Stress Testing

**Date:** September 19, 2026  
**Auditor:** Time-Series Validation Scientist, Senior ML Research Scientist  
**Principle:** In maritime telemetry, naive random $k$-fold cross-validation is fundamentally invalid due to temporal auto-correlation and vessel-specific hull dynamics. Multi-dimensional stress validation is mandatory.  

---

## 1. Five-Tier Validation Protocol Architecture

Phase 6 implements a rigorous five-tier validation protocol:

```
                      [Real Telemetry (173,974 Records)]
                                     │
         ┌──────────────┬────────────┴────────────┬─────────────┐
         ▼              ▼                         ▼             ▼
       [V1]           [V2]                      [V3]          [V4]
   Forward        Rolling-Origin             Leave-One-     Regime-
   Temporal        Cross-Val                 Vessel-Out    Stratified
  (60/20/20)    (3 Shift Windows)             (LOVO)       (4 Modes)
                                                  │
                                                  ▼
                                                [V5]
                                            Out-of-Domain
                                             Stress Test
                                         (Mahalanobis >95%)
```

---

## 2. Experimental Execution & Quantitative Findings

### 2.1 Protocol V1: Forward Temporal Validation
- **Setup:** Contiguous chronological partitioning per vessel (60.0% Train = 104,384 rows; 20.0% Val = 34,794 rows; 20.0% Test = 34,796 rows).
- **Purpose:** Assesses out-of-sample forward-in-time forecasting under physical seasonal drift and natural biofouling accumulation over a 12-month period.
- **Results:**
  - P2 Baseline: $\text{MAE} = 246.97\text{ kg/h}$, $R^2 = 0.9501$.
  - QI-C1 (QIEA-FS): $\text{MAE} = 237.96\text{ kg/h}$, $R^2 = 0.9530$.
  - Temporal error degradation over the 12-month horizon is $+3.8\%$ (minimal seasonal drift).

### 2.2 Protocol V2: Rolling-Origin Cross-Validation
- **Setup:** Three expanding temporal windows:
  - Window 1: Train 0–50% (86,987 rows) $\to$ Test 50–65% (26,096 rows).
  - Window 2: Train 0–65% (113,083 rows) $\to$ Test 65–80% (26,096 rows).
  - Window 3: Train 0–80% (139,179 rows) $\to$ Test 80–100% (34,795 rows).
- **Quantitative Results:**
  - Window 1 MAE: $254.12\text{ kg/h}$ ($R^2 = 0.9465$)
  - Window 2 MAE: $249.80\text{ kg/h}$ ($R^2 = 0.9482$)
  - Window 3 MAE: $244.30\text{ kg/h}$ ($R^2 = 0.9515$)
- **Scientific Finding:** Performance steadily improves as the training window expands, confirming monotonic learning stability and absence of concept drift catastrophe.

### 2.3 Protocol V3: Leave-One-Vessel-Out (LOVO) Cross-Vessel Generalization
- **Central Scientific Question:** Can a model trained on two vessels accurately predict fuel consumption on a completely unseen third vessel?
- **Setup:**
  - Fold 1: Train on *CPS_Triton* + *OSS_Ceto* $\to$ Test on unseen *CPS_Poseidon*.
  - Fold 2: Train on *CPS_Poseidon* + *OSS_Ceto* $\to$ Test on unseen *CPS_Triton*.
  - Fold 3: Train on *CPS_Poseidon* + *CPS_Triton* $\to$ Test on unseen *OSS_Ceto*.
- **Quantitative Results:**

| Test Vessel (Unseen) | Baseline P2 MAE (kg/h) | Baseline P2 $R^2$ | QI-C1 (QIEA) MAE (kg/h) | QI-C1 $R^2$ | In-Domain Test MAE (Ref) | Cross-Vessel Degradation Factor |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CPS_Poseidon** | **1,124.50 kg/h** | **0.2410** | **1,098.20 kg/h** | **0.2580** | 331.26 kg/h | **3.40x error increase** |
| **CPS_Triton** | **385.40 kg/h** | **0.1850** | **372.10 kg/h** | **0.2015** | 74.40 kg/h | **5.18x error increase** |
| **OSS_Ceto** | **592.80 kg/h** | **-0.4120** | **581.40 kg/h** | **-0.3850** | 210.77 kg/h | **2.81x error increase** |

#### Crucial Scientific Honesty Verdict:
**LOVO performance is POOR across both classical and quantum-inspired models.**
Zero-shot cross-vessel generalization between fundamentally different hull types (e.g., training on container ships and testing on a bulk carrier) **FAILS**. 
Neither classical ML nor quantum-inspired feature selection can overcome the physical reality that different vessels possess unique block coefficients, engine tuning, propeller geometries, and auxiliary baseline draws.
**Strict Rule Enforced:** This is reported honestly. We categorically REJECT claiming that either model "generalizes zero-shot across unseen vessel classes." Operational deployment requires vessel-specific calibration.

### 2.4 Protocol V4: Operational Regime Stratification
Telemetry is partitioned into four distinct operating regimes:
1. **Cruising ($V_{STW} \ge 8.0\text{ kn}$):** P2 MAE = $218.45\text{ kg/h}$ ($R^2 = 0.9612$); QI-C1 MAE = $209.12\text{ kg/h}$ ($R^2 = 0.9645$).
2. **Maneuvering ($2.0 \le V_{STW} < 8.0\text{ kn}$):** P2 MAE = $312.60\text{ kg/h}$; QI-C1 MAE = $304.85\text{ kg/h}$.
3. **Stopped / Berthing ($V_{STW} < 2.0\text{ kn}$):** P2 MAE = $142.10\text{ kg/h}$; QI-C1 MAE = $139.50\text{ kg/h}$.
4. **Rough Sea ($H_s \ge 3.0\text{ m}$):** P2 MAE = $425.80\text{ kg/h}$; QI-C1 MAE = $411.20\text{ kg/h}$.

### 2.5 Protocol V5: Out-of-Distribution (OOD) Stress Testing
- Identified via Mahalanobis distance $D_M(x) = \sqrt{(x - \mu)^T \Sigma^{-1} (x - \mu)}$ on continuous kinematic and weather features.
- Out-of-Distribution threshold set to the 95th percentile of the training distribution.
- **In-Domain ($\le 95$th percentile, 33,056 rows):** MAE = $235.10\text{ kg/h}$ (P2), $226.45\text{ kg/h}$ (QI-C1).
- **Out-of-Domain ($>95$th percentile, 1,740 rows):** MAE = $472.50\text{ kg/h}$ (P2), $458.12\text{ kg/h}$ (QI-C1).
- **Degradation:** Error increases by $\sim 101\%$ in extreme OOD regions.
- **Safety Mitigation:** The `DomainChecker` triggers an OOD alert and expands prediction intervals by $2.5\times$ when inputs exceed $D_{M, 95}$.
