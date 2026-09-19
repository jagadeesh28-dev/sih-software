# Quantum-Inspired Differential Evolution (QIDE) Benchmark
**Algorithm:** Differential Evolution with Quantum Rotation Gate Mutation Operator
**Test Hypothesis:** Quantum rotation angle updates improve continuous DE mutation.

## 1. Experimental Comparison

| Algorithm | Feasibility | Physical Objective | Convergence Iteration | Wall-Clock Time |
| :--- | :--- | :--- | :--- | :--- |
| **Standard Classical DE** | **100.0%** | **3.70** | **238 evals** | **1.71s** |
| **QIDE (Rotation Angle)** | 100.0% | 3.78 | 265 evals | 3.15s |
| **Wilcoxon p-value** | - |  = 0.684$ (No significant difference) | - | - |

## 2. Audit Verdict
- **No Practical Value Added:** QIDE introduces trigonometric angle mapping onto continuous box domains without yielding any statistically significant improvement over standard vector difference mutation ( = x_{r1} + F(x_{r2} - x_{r3})$).
- **Classification:** MARKED AS BENCHMARK-ONLY. QIDE is retained in the test suite for historical completeness but excluded from operational production.
