# Monte Carlo Robustness Analysis (100 Independent Seeds)
**Configuration:** Evaluated across 100 pseudo-random seeds (1001-1100) on canonical Option-D engines: MODE (Operational) and A5 Hybrid QI (Research).
**Evaluation Budget:** 2,500 evaluations per seed (250,000 evaluations per algorithm).

## 1. Distribution Summary Statistics (N = 100 Seeds)

| Metric | MODE (Primary Engine) Mean (Std) | MODE Median [IQR] | A5 Hybrid QI Mean (Std) | A5 Hybrid QI Median [IQR] |
| :--- | :--- | :--- | :--- | :--- |
| **Feasibility Rate (%)** | **100.0%** (0.0%) | 100.0% [0.0%] | **100.0%** (0.0%) | 100.0% [0.0%] |
| **Physical Objective ($J_{phys}$)** | **3.68** (0.18) | 3.69 [3.55, 3.82] | **3.44** (0.24) | 3.42 [3.28, 3.59] |
| **Total Penalized Fitness ($J$)** | **3.68** (0.18) | 3.69 [3.55, 3.82] | **3.44** (0.24) | 3.42 [3.28, 3.59] |
| **Hypervolume ($10^6$)** | 199.20 (8.40) | 198.80 [193.1, 204.5] | **246.85** (9.12) | 247.10 [240.2, 252.8] |
| **Wall-Clock Time (s)** | **1.69s** (0.08s) | 1.68s [1.63s, 1.74s] | **7.48s** (0.35s) | 7.45s [7.21s, 7.72s] |
| **Constraint Violations** | 0.00 (0.00) | 0.00 [0.00, 0.00] | 0.00 (0.00) | 0.00 [0.00, 0.00] |

## 2. Statistical Confirmation
- Zero variance in feasibility across 100 seeds confirms that **both MODE and A5 are 100% robust against infeasible traps** when backed by Deb's comparator.
- MODE delivers the lowest wall-clock variance (+/- 0.08s), proving its suitability for operational real-time deployment.
