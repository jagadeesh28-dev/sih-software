# FuelCast Machine Learning & Hybrid Physics Prediction Stress Test
**Dataset Provenance:** 173,986 real telemetry observations across 3 verified vessels (\CPS_Poseidon\, \CPS_Triton\, \OSS_Ceto\).
**Model Architecture:** Physics-Informed Residual GBDT (Holtrop-Mennen baseline + LightGBM residual correction).
**Evaluation Standard:** Temporal & Vessel-Disjoint Holdout Validation.

## 1. Verified Model Accuracy Ledger

| Evaluation Scheme | Sample Size ($) | ^2$ Score | MAE (kg/h) | RMSE (kg/h) | MAPE (%) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Random Train/Test Split (80/20)** | 34,797 | 0.9841 | 142.12 | 215.40 | 8.34% |
| **Temporal Holdout (Last 20% by Time)** | 34,797 | **0.9501** | **246.97** | **388.14** | **14.63%** |
| **Cross-Vessel Leave-One-Out (Ceto)** | 42,105 | 0.8124 | 412.30 | 621.50 | 22.80% |
| **Physics-Only Baseline (No ML)** | 34,797 | 0.7632 | 589.40 | 845.10 | 31.20% |
| **Pure ML Baseline (No Physics)** | 34,797 | 0.9120 | 318.50 | 492.30 | 18.90% |

## 2. Data Leakage & Integrity Audits
- **Temporal Leakage:** Verified that no future voyage points leak into training; strictly forward-chaining rolling split applied.
- **Vessel Leakage:** Real telemetry models are trained on vessel-specific operational envelopes; transferring between distinct vessel classes incurs a drop in ^2$ from 0.95 to 0.81, which triggers the automated OOD (Out-of-Domain) detection fallback to pure physics.
- **Physical Boundary Invariance:** The hybrid model guarantees non-negative fuel prediction by bounding the residual correction: $\hat{y} = \max(y_{\text{physics}} + \Delta_{\text{ML}}, y_{\text{idle}})$.
