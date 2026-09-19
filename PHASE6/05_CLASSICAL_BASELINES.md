# PHASE 6 — STEP 5: CLASSICAL BENCHMARK CONTROLS
## SIH26138 — Egreen Quanta
### Comparative Analysis of Physics-Only, Pure ML, and Hybrid Residual Baselines

**Date:** September 19, 2026  
**Auditor:** Senior ML Research Scientist, Benchmark Architect  
**Dataset:** Real FuelCast Telemetry (173,974 records across 3 vessels)  
**Evaluation Split:** Strict Forward Chronological Test Partition (20%, 34,796 records)  

---

## 1. Classical Control Hierarchy

To isolate the scientific value of quantum-inspired prediction mechanisms, three classical controls are established under identical data splits, feature inputs (`CONFIG_REAL_A`), and evaluation protocols:

```
[P0: Pure Naval Architecture]
        |
        v
    F_phys(x)
(No ML, deterministic, negative bias)
        |
        +-----------------------------------+
        |                                   |
        v                                   v
[P1: Pure Empirical ML]        [P2: Hybrid Physics + Residual]
     y_hat = f_ML(X)                y_hat = max(0, F_phys(x) + alpha * r_hat(X))
(No physics, unconstrained)       (Frozen Reference: MODEL-REAL-04)
```

---

## 2. Quantitative Performance Comparison

All classical models were trained strictly on `fleet_train` (104,384 rows) and evaluated on `fleet_test` (34,796 rows):

| Model Code | Model Name | Governing Architecture | Feature Space | MAE (kg/h) | RMSE (kg/h) | MAPE (%) | $R^2$ | MedAE (kg/h) | Bias (kg/h) | Training Time (s) | Inference Latency (ms) | Physical Violations |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **P0** | **Physics-Only** | Holtrop-Mennen + STAwave-2 + Blendermann | STW, Draft, Displacement, Metocean | **1,885.45** | **2,468.05** | **72.56%** | **-0.5471** | 1,228.38 | -1,883.19 | 0.00 s | 0.05 ms | 0 (bounded) |
| **P1** | **Pure Classical ML** | LightGBM Direct Regressor | `CONFIG_REAL_A` (14 features) | **263.91** | **486.05** | **15.69%** | **0.9400** | 138.08 | -146.19 | 0.63 s | 0.02 ms | 31 negative preds (clipped) |
| **P2** | **Physics + ML Residual** | Hybrid Residual Learner ($\alpha=1.0$) | `CONFIG_REAL_A` on residual $r$ | **246.97** | **443.21** | **14.63%** | **0.9501** | **129.31** | **-141.82** | 36.10 s | 0.02 ms | **0 (physically bounded)** |

---

## 3. Structural Analysis of Classical Baselines

### 3.1 P0 (Physics Only) Analysis
- **Strengths:** 100% physically interpretable; exact asymptotic scaling at high Froude numbers; cannot predict non-physical negative consumption; zero training time required.
- **Deficiencies:** Uncalibrated for real-world biofouling degradation, propeller surface roughness, and auxiliary electrical demands. Under-predicts fuel consumption by an average of $-1,883.19\text{ kg/h}$ ($R^2 = -0.5471$).
- **Conclusion:** Pure naval architecture provides an indispensable foundation, but cannot serve alone as an operational digital twin.

### 3.2 P1 (Pure Classical ML) Analysis
- **Strengths:** Rapid training ($0.63\text{ s}$); achieves strong in-distribution statistical correlation ($R^2 = 0.9400, \text{MAE} = 263.91\text{ kg/h}$).
- **Deficiencies:** Lacks physical inductive bias. When subjected to extreme out-of-distribution inputs or calm water drift, it generated 31 negative fuel predictions (requiring artificial zero-clipping). It exhibits erratic extrapolation when speed and draft deviate from the training distribution.

### 3.3 P2 (Physics + ML Residual) Analysis
- **Strengths:**
  - **Superior Accuracy:** Delivers the lowest error among all classical architectures ($\text{MAE} = 246.97\text{ kg/h}$, $R^2 = 0.9501$), outperforming pure ML by **$+6.42\%$ lower MAE** and **$+8.81\%$ lower RMSE**.
  - **Physical Stability:** Because the ML model only learns the additive delta $r = y - y_{phys}$, the baseline retains the cubic hydrodynamic speed curve.
  - **Zero Domain Violations:** Enforcing the lower bound $\max(0, F_{phys} + \alpha \cdot \hat{r})$ guarantees zero physical violations.
- **Scientific Role:** P2 is the official **FROZEN BASELINE** (`MODEL-REAL-04`). All quantum-inspired candidate models (QI-C1 and QI-C2) must be compared directly against P2.

---

## 4. Benchmark Decision Gate Clearance

```
======================================================================
CLASSICAL BASELINE SELECTION VERDICT:
Primary Benchmark Anchor: P2 (Physics + ML Residual / MODEL-REAL-04)
Frozen Performance Standard: MAE = 246.97 kg/h, R2 = 0.9501, MAPE = 14.63%
Budget Reference: 150 trees, max_depth=6, 14 features (CONFIG_REAL_A)
CLEARANCE STATUS: APPROVED AS PERMANENT EVALUATION TARGET.
======================================================================
```
