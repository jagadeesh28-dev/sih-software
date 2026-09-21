# Slide 4: Predictive Modeling — Physics Baseline vs QI-C1

## Dual-Path Predictive Architecture

```
                      Input Environmental & Telemetry Features (x)
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
     ┌────────────────────────┐                     ┌────────────────────────┐
     │  First-Principles      │                     │  Residual Predictor    │
     │  Physics Model         │                     │  QI-C1 / QI-C1-VT      │
     │  (Holtrop-Mennen + kW) │                     │  (LightGBM Booster)    │
     └───────────┬────────────┘                     └───────────┬────────────┘
                 │ f_phys(x)                                    │ r_pred(x)
                 └───────────────────────┬──────────────────────┘
                                         ▼
                             Predicted Fuel Flow F(x) =
                             max(0, f_phys(x) + r_pred(x))
```

---

## 30-Seed Matched Baseline Evaluation

| Model Identifier | Features | Architecture | Seed 42 MAE | 30-Seed Mean MAE | 30-Seed Mean $R^2$ |
|:---|:---:|:---|---:|---:|---:|
| **Pure Physics** | 12 | First-principles Holtrop-Mennen | 1,885.45 kg/h | 1,885.45 kg/h | -0.5471 |
| **MODEL-REAL-04** | 14 | Reference Anchor LightGBM | 246.91 kg/h | 248.12 ± 0.81 kg/h | 0.9501 ± 0.0003 |
| **QI-C1 (Original)**| 6 | QIEA Selected Subset + LightGBM | **244.86 kg/h** | **237.96 ± 5.46 kg/h** | **0.9530 ± 0.0018** |
| **QI-C1-vessel-type**| 7 | QIEA Subset + Categorical `vessel_type` | 252.77 kg/h | 252.62 ± 1.70 kg/h | 0.9478 ± 0.0004 |

---

## Conformal Uncertainty Calibration (90% Nominal Confidence)
- **MODEL-REAL-04**: Empirical coverage = 95.05%, Interval Width = 2,273.70 kg/h.
- **QI-C1-vessel-type**: Empirical coverage = **93.24%**, Interval Width = **1,641.69 kg/h** (**27.80% sharper**).
- **Statistical Guarantee**: Finite-sample distribution-free validity without Gaussian error assumptions.
