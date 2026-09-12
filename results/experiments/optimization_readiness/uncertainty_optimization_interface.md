# Uncertainty-to-Optimization Interface Analysis
**Document ID:** `AUDIT-UNC-INTERFACE-001`  
**Formulation:** J(lambda) = q50 + lambda * (q95 - q05)  
**Software Version:** 0.2.1 | **Git Commit:** `febed1ae38a3b2be34235dc6436b5fc7d493808b`  

---

## 1. Candidate Robust Objective Evaluation

| lambda (Risk Aversion) | Mean J(lambda) (kg/h) | Median J(lambda) (kg/h) | Mean Uncertainty Width (kg/h) |
| :---: | :---: | :---: | :---: |
| 0.00 | 351.12 | 345.44 | 54.40 |
| 0.25 | 364.72 | 352.76 | 54.40 |
| 0.50 | 378.32 | 360.08 | 54.40 |
| 1.00 | 405.53 | 374.72 | 54.40 |
| 2.00 | 459.93 | 446.15 | 54.40 |

---

## 2. Key Insights for Phase 3 Fleet Optimization
1. **lambda = 0.0 (Risk-Neutral)**: Uses median prediction q50.
2. **lambda = 0.5 (Balanced Robustness - Recommended)**: Penalizes high-dispersion routes while retaining operational efficiency.
3. **lambda = 1.0 (Conservative)**: Approximates q95, safeguarding against unexpected fuel exhaustion or CII penalties.
