# Classical Differential Evolution (DE / MODE) Stress Test
**Algorithm:** DE/rand/1/bin and Multi-Objective Differential Evolution (MODE)
**Status:** PRIMARY OPERATIONAL ENGINE VALIDATED.

## 1. Parameter Sensitivity & Robustness (30 Seeds Matched)

| Configuration (, CR$) | Feasibility Rate | Mean Physical Objective | Convergence Speed ({90}$) | Wall-Clock Time (s) |
| :--- | :--- | :--- | :--- | :--- |
|  = 0.5, CR = 0.3$ | 100.0% | 4.25 | 185 evals | 1.62s |
|  = 0.7, CR = 0.5$ | 100.0% | 3.92 | 210 evals | 1.68s |
| ** = 0.8, CR = 0.9$ (Default)**| **100.0%** | **3.70** | **238 evals** | **1.71s** |
|  = 0.9, CR = 0.9$ | 100.0% | 4.10 | 280 evals | 1.75s |

## 2. Operational Engine Merits
1. **Physical Fitness Champion:** Achieves lowest mean physical objective (.70$) with lowest variance among all single-objective optimizers.
2. **Computational Speed:** 1.706 seconds per 2,500 evaluations (4.4x faster than Full Hybrid QI A5 at 7.514s).
3. **Zero Stagnation:** In 30/30 runs, DE never collapsed into an infeasible basin when coupled with Deb's feasibility-first comparison.
4. **Primary Engine Selection:** Justifies Case A/B in the architecture decision framework: DE is the primary workhorse for real-time operational voyage dispatch.
