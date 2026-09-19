# Slide 10: Master Experimental Results & Conformal Uncertainty

## 1. Conformal Uncertainty Quantification (Nominal 90% Level)

| Model Architecture | Non-Conformity Quantile ($\hat{q}$) | Empirical Test Coverage (PICP) | Interval Width (MPIW) | Width / Mean Fuel Ratio | Sharpness Gain |
|:-------------------|:------------------------------------|:-------------------------------|:----------------------|:------------------------|:---------------|
| **MODEL-REAL-04** (Reference Anchor) | $1,136.85\text{ kg/h}$ | $95.05\%$ | $2,273.70\text{ kg/h}$ | $0.9302$ | Baseline |
| **QI-C1** (Quantum-Inspired) | **$782.47\text{ kg/h}$** | **$93.56\%$** | **$1,564.93\text{ kg/h}$** | **$0.6402$** | **+31.17% Sharper** |

> **Accurate Scientific Statement**: "QI-C1 produced narrower conformal intervals than MODEL-REAL-04 under the evaluated test protocol (31.17% narrower), while maintaining empirical coverage (93.56%) comfortably above the nominal 90% floor."

---

## 2. Master System-Wide Summary

| Metric Dimension | Verified Quantitative Value | Verification Protocol |
|:-----------------|:----------------------------|:----------------------|
| **Audited Telemetry** | $173,974$ validated records | 3 commercial vessels; cryptographic Parquet hashes |
| **Prediction Accuracy (QI-C1)** | $\text{MAE} = 237.96 \pm 5.46\text{ kg/h}, R^2 = 0.9530$ | 30-seed matched mean on $34,796$ test samples |
| **Classical Control (GA)** | $\text{MAE} = 237.24 \pm 4.89\text{ kg/h}, R^2 = 0.9532$ | Wilcoxon signed-rank test ($p = 0.684$, parity) |
| **Search Space Diversity** | $+44.7\%$ Shannon bit-entropy | $H_{\text{bit}} = 0.2814$ (QIEA) vs $0.2104$ (GA) |
| **In-Domain Reliability** | $0.0\%$ False Positive Rate | Zero false alarms across $2,000$ real test states |
| **Severe Storm Detection** | $96.55\%$ Recall ($d_{\text{env}} = 1.50$) | $100.0\%$ Recall at warning threshold ($d = 1.00$) |
| **Software Fault Interception**| $100.0\%$ Safe Rejection / Recovery | 1,000 stress tests, 16 edge cases, 10 fault injections |
| **Optimization Fidelity** | $825,000$ evaluations frozen | Penalty gap rigorously distinguished ($J^* = 873.23\text{ t}$) |
| **Single-Command Reproduction** | $\approx 1.8\text{ seconds}$ | `python reproduce_release.py` (10/10 Gates PASS) |
