# AUDIT #4: OBJECTIVE SCALE FORENSICS & FORMULATION RECONCILIATION
**Project:** SIH26138 — Egreen Quanta  
**Audit Section:** §6 Objective Scale Forensics & Dimensional Consistency  
**Auditors:** Senior Optimization Research Scientist & Mathematical Methods Auditor  
**Date:** September 15, 2026  

---

## 1. The Core Scientific Anomaly

In Phase 5 documentation, a striking apparent discrepancy was detected between two reported values:
1. **Level 1 Small-Scale Exact Global Optimum:** $J^* = 873.2265$ reported in `small_exact.csv`.
2. **Main Benchmark Physical Objectives:** $J_{\text{phys}} \approx 3.45$ (A5) and $3.70$ (DE) reported in `A5_ABLATION_TABLE.csv`.
3. **Reported Optimality Gap:** $0.0\%$ reported for A1, A2, A4, and A5.

A superficial reading raises immediate skepticism: *How can an algorithm achieving an objective of $3.45$ claim a $0.0\%$ optimality gap against a global optimum of $873.23$?*

---

## 2. Forensic Code Trace & Root Cause Analysis

A line-by-line trace of `src/validation/small_exact.py` and `optimization/fleet_evaluator_phase4.py` revealed the exact mathematical mechanism behind this divergence:

### 2.1 The Definition of Physical Objective ($J_{\text{phys}}$)
In `Phase4FleetEvaluator.evaluate_vector()`, the physical objective is a **dimensionless, multi-criteria robust loss**:
$$J_{\text{phys}} = \sum_{k=1}^4 w_k \left( \frac{\text{Metric}_k}{\text{Scale}_k} \right) + \lambda \cdot \text{CVaR}_{0.80}(\text{Loss})$$
where the reference normalization scales are:
$$\mathbf{Scale} = [50.0\text{ tonnes}, \$50,000, 150.0\text{ tonnes}, 10.0\text{ hours}, \$10,000]$$
and the objective weights are:
$$\mathbf{w} = [0.30, 0.30, 0.25, 0.10, 0.05]$$
Because each operational metric is normalized by its expected fleet scale, **$J_{\text{phys}}$ is dimensionless and naturally resides in the numerical range $[3.0, 5.0]$**.

### 2.2 The Definition of Total Fitness ($\text{Fitness}$)
Total penalized fitness is defined in `Phase4FleetEvaluator` as:
$$\text{Fitness} = J_{\text{phys}} + \text{Total Penalty}$$
where $\text{Total Penalty}$ includes:
- Hard constraint violations: $\$50,000$ per violation.
- Soft schedule delay penalties: $\$1,500$ per hour of delay past the charter window.

### 2.3 The Formulation Mismatch in `small_exact.py`
In `src/validation/small_exact.py`:
1. **The Grid Search (lines 55–60):**
   ```python
   res = evaluator.evaluate_vector(x_cand)
   if res.is_feasible and res.fitness < exact_best_score:
       exact_best_score = float(res.fitness)
   ```
   The grid search searched for the candidate minimizing **`res.fitness`** (penalized total fitness). In that restricted 3-vessel subspace, the best candidate had a pure physical loss of $3.7861$, but incurred a soft schedule delay penalty of **$\$869.44$** on Demand-C. Hence:
   $$\text{exact\_best\_score} = 3.7861 + 869.44 = 873.2265$$
   However, the true unpenalized physical minimum in that exact grid search was **$J^*_{\text{phys}} = 3.2369$**!

2. **The Metaheuristic Algorithm Loop (lines 94–100):**
   ```python
   score = float(res.best_physical_objective if res.feasible_at_end else res.best_fitness)
   ...
   gap = max(0.0, (mean_score - exact_best_score) / exact_best_score)
   ```
   When feasible algorithms (A1, A2, A4, A5) succeeded, `score` was assigned `best_physical_objective` ($\approx 3.16$ to $4.75$), whereas `exact_best_score` remained $873.2265$!
   $$\Delta = \frac{3.1666 - 873.2265}{873.2265} = -0.9963 \quad (< 0)$$
   The expression `max(0.0, (mean_score - exact_best_score) / exact_best_score)` clipped this negative value to **$0.0\%$**!

---

## 3. Independent Recalculation & Reconciliation

To establish complete scientific honesty, we recompute the exact comparisons under consistent definitions:

### Metric Comparison Table
| Comparison Framework | Exact Ground Truth $J^*$ | A1 (QPSO+Deb) | A2 (QPSO+Repair) | A4 (Hetero QI) | A5 (Complete QI) | DE (Classical) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **A. Pure Physical Loss ($J_{\text{phys}}$)** | **$3.2369$** | $3.1666$ | $3.4205$ | $4.7544$ | $4.5203$ | $3.3812^*$ |
| **Physical Optimality Gap (%)** | — | **$0.00\%$** (Found better speed) | **$+5.67\%$** | **$+46.88\%$** | **$+39.65\%$** | **$+4.46\%$** |
| **B. Total Penalized Fitness ($\text{Fitness}$)**| **$873.2265$** | $3.1666$ (Zero delay) | $3.4205$ (Zero delay) | $4.7544$ (Zero delay) | $4.5203$ (Zero delay) | $17,001.53$ (1 fail) |
| **Penalized Optimality Gap (%)** | — | **$0.00\%$** | **$0.00\%$** | **$0.00\%$** | **$0.00\%$** | **$+1,846.98\%$** |

*\*Note: For DE, 2 out of 3 runs achieved feasible physical loss of $3.3812$, while 1 run incurred a $\$50,000$ assignment penalty on budget 500.*

---

## 4. Key Takeaways & Required Scientific Corrections

1. **The 0.0% gap was NOT fabricated; it was an apples-to-oranges metric clipping error.**
2. When evaluating on **Total Penalized Fitness**, the metaheuristics discovered routes with **zero schedule delay**, achieving fitness $\approx 3.4$ to $4.5$, outperforming the grid search's $873.23$ because continuous cruising speed optimization avoided the discrete grid's port arrival delay.
3. When evaluating on **Pure Physical Loss**, A1 achieved $3.1666$ ($0.0\%$ gap vs. grid's $3.2369$), A2 achieved $3.4205$ ($5.67\%$ gap), and A5 achieved $4.5203$ ($39.65\%$ gap within 500 evaluations).
4. **Mandatory Documentation Correction:** All references to "0.0% optimality gap" in `PHASE5_FINAL_REPORT.md` and `PHASE5_SIH_STORY.md` must be transparently clarified to distinguish between *pure physical loss* and *total penalized fitness*.
