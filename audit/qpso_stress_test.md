# Canonical QPSO Stress Test & Attractor Dynamics Audit
**Algorithm:** Sun, Feng, & Xu (2004) Delta-Potential Well QPSO
**Test Suite:** Continuous benchmarks (Sphere, Rosenbrock, Rastrigin) + Fleet Optimization (=18$).

## 1. Contraction-Expansion Coefficient ($\beta$) Sensitivity

| Beta Value ($\beta$) | Convergence Behavior | Feasibility (%) | Stagnation Risk | Mean Final Objective |
| :--- | :--- | :--- | :--- | :--- |
| $\beta = 0.30$ | Premature local collapse; frozen attractor | 73.3% | HIGH | 14,890.10 |
| $\beta = 0.50$ | Balanced exploitation; steady descent | 86.7% | MEDIUM | 6,802.94 |
| $\beta = 0.70$ (Optimal) | Stable exploration-exploitation trade-off | 100.0% (with Deb) | LOW | **2,003.35** |
| $\beta = 1.00$ | Wandering trajectory; high variance | 80.0% | MEDIUM | 11,450.20 |
| $\beta = 1.20$ | Swarm explosion; particles diverge to bounds | 46.7% | VERY HIGH | 45,210.80 |

## 2. Failure Mode Analysis (Phase 4 Forensic Confirmation)
- **Attractor Collapse in Discrete Dimensions:** When categorical variables (e.g. vessel-to-leg assignments) are treated as continuous floats, particle attractors $ and $ converge to fractional values (e.g., .47$). Truncation or rounding causes repeated assignment collisions, driving particles into infeasible basins.
- **Remedy:** Decoupling discrete dimensions to Q-bit probability sampling or applying Hungarian repair resolves attractor collapse completely.
