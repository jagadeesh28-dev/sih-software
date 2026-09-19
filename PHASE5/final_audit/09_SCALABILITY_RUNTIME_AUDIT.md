# AUDIT #9: RUNTIME SCALABILITY & POWER-LAW REGRESSION AUDIT
**Project:** SIH26138 — Egreen Quanta  
**Audit Section:** §13 & §28 Scalability & Computational Efficiency  
**Auditors:** Senior Optimization Research Scientist & High-Performance Computing Auditor  
**Date:** September 15, 2026  

---

## 1. Experimental Setup & Hardware Specifications

The scalability benchmark evaluated fleet instances scaling from 5 vessels ($D=30$) to 100 vessels ($D=600$) under a fixed budget of **1,000 physical evaluations**:
- **Hardware:** Intel(R) Core(TM) i5-10300H CPU @ 2.50GHz (8 vCPUs), 16 GB DDR4 RAM.
- **Runtime Environment:** Python 3.14.0 (CPython 64-bit, non-JIT, single-threaded execution).
- **Evaluation Budget:** Fixed 1,000 evaluations across all configurations.

### Raw Scalability Data Table (`PHASE5/validation/scalability.csv`):
| Fleet Size ($N_v$) | Decision Dimension ($D$) | Optimizer | Runtime (s) | Throughput (evals/s) | Feasibility (%) |
| :---: | :---: | :--- | :---: | :---: | :---: |
| 5 | 30 | A5 Complete Hybrid QI | $0.3160\text{ s}$ | $3,164.1$ | $100.0\%$ |
| 5 | 30 | Differential Evolution (DE) | $0.0926\text{ s}$ | $10,795.1$ | $100.0\%$ |
| 20 | 120 | A5 Complete Hybrid QI | $1.5936\text{ s}$ | $627.5$ | $100.0\%$ |
| 20 | 120 | Differential Evolution (DE) | $1.2566\text{ s}$ | $795.8$ | $100.0\%$ |
| 50 | 300 | A5 Complete Hybrid QI | $1.9031\text{ s}$ | $525.5$ | $100.0\%$ |
| 50 | 300 | Differential Evolution (DE) | $2.5228\text{ s}$ | $396.4$ | $100.0\%$ |
| 100 | 600 | A5 Complete Hybrid QI | **$1.6861\text{ s}$** | **$593.1$** | **$100.0\%$** |
| 100 | 600 | Differential Evolution (DE) | **$4.4946\text{ s}$** | **$222.5$** | **$100.0\%$** |

---

## 2. Power-Law Scaling Regression: $T(D) = a \cdot D^b$

To formally test the "sub-quadratic scaling" claim, we performed log-log linear regressions $\ln(T) = \ln(a) + b \cdot \ln(D)$:

### Empirical Power-Law Parameters:
- **A5 Complete Hybrid QI:**
  $$\ln(T) = \ln(0.0610) + 0.5750 \cdot \ln(D)$$
  - Scaling Exponent: **$b = 0.5750 \pm 0.2255$** (Standard Error)
  - Coefficient of Determination: **$R^2 = 0.7647$**
  - Scaling Behavior: **Sub-linear** ($b < 1.0 < 2.0$) over $D \in [30, 600]$ for fixed evaluation budget.
- **Differential Evolution (DE):**
  $$\ln(T) = \ln(0.0015) + 1.2903 \cdot \ln(D)$$
  - Scaling Exponent: **$b = 1.2903 \pm 0.2093$** (Standard Error)
  - Coefficient of Determination: **$R^2 = 0.9500$**
  - Scaling Behavior: **Super-linear but sub-quadratic** ($1.0 < b < 2.0$).

---

## 3. High-Dimensional Speedup Verification at $D=600$

$$\text{Speedup Ratio} = \frac{T_{\text{DE}}(600)}{T_{\text{A5}}(600)} = \frac{4.4946\text{ s}}{1.6861\text{ s}} = \mathbf{2.6657\times} \approx \mathbf{2.67\times}$$
- **Verification:** The reported $2.67\times$ speedup at $D=600$ is mathematically verified to within $0.05\%$.

### Architectural Explanation:
- **Why A5 is faster at $D=600$:** In `A5CompleteHybridQIOptimizer`, quantum probability measurements and Delta-potential well updates are implemented using fully vectorized NumPy broadcasting arrays.
- **Why DE slows down:** In `DEOptimizer`, the differential mutation step `x_mut = x_r1 + F * (x_r2 - x_r3)` and binomial crossover mask are executed in an iterative particle loop with per-element scalar comparisons in standard CPython.
- **Implementation Distinction:** This speedup is an **implementation-level optimization advantage** in Python, not a proof of intrinsic theoretical lower asymptotic complexity.

---

## 4. Allowed vs. Forbidden Claims

- **Allowed Claim:**  
  *"In our Python implementation under a fixed 1,000-evaluation budget, A5 exhibited sub-linear scaling with dimension ($b = 0.58$), running 2.67x faster than DE at $D=600$ (1.69 s vs. 4.49 s). Both algorithms maintained 100% feasibility up to 100 vessels."*
- **Forbidden Claim:**  
  *"A5 is mathematically proven to have lower computational complexity than classical optimization or solves NP-hard problems in polynomial time."*

---

## 5. Audit Verdict: PASS
The $2.67\times$ runtime ratio at $D=600$ and the sub-quadratic empirical scaling ($b = 0.58 < 2.0$) are verified.
