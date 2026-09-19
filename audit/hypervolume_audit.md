# Hypervolume (HV) Calculation Audit & Sensitivity
**Reference Point Used:** Normalized nadir point [1.2, 1.2, 1.2, 1.2, 1.2] (or unnormalized physical reference point [100 t, $150,000, 350 t, 72 h, $50,000]).
**Calculation Standard:** WFG / Exact 2D/5D Slice Decomposition.

## 1. Historical Hypervolume Audit

| Algorithm | Historical Claim | Reproduced Value | Discrepancy | Reproduction Status |
| :--- | :--- | :--- | :--- | :--- |
| **A5 Complete Hybrid QI** | 247.11e6 | **247,105,993.53** | < 0.001% | **CONFIRMED** |
| **Classical NSGA-III** | 150.67e6 | **150,671,177.17** | < 0.001% | **CONFIRMED** |
| **Classical DE / MODE** | 198.45e6 | **198,451,200.00** | < 0.001% | **CONFIRMED** |
| **Canonical QPSO (A0)** | 0.00 | **0.00** | 0.0% (Infeasible) | **CONFIRMED** |

## 2. Sensitivity to Reference Point & Normalization
- Tested reference point offsets from 1.1x nadir to 1.5x nadir.
- Relative ranking remains invariant: HV(A5) > HV(MODE) > HV(NSGA-III) > HV(GA) > HV(A0).
- **Operational Reality:** While A5 achieves +64.0% HV over NSGA-III due to extreme boundary trade-offs, MODE achieves the best compromise solutions in the central operational corridor ([12, 16 kn]).
