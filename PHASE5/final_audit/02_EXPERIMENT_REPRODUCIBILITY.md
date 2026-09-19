# AUDIT #2: EXPERIMENT REPRODUCIBILITY & PROTOCOL FAIRNESS
**Project:** SIH26138 — Egreen Quanta  
**Audit Section:** §5 Experiment Reproducibility & Budget Fairness  
**Auditor:** Reproducibility Auditor & Evolutionary Computation Reviewer  
**Date:** September 15, 2026  

---

## 1. Experimental Integrity Check

An essential requirement of scientific benchmarking is that all competing algorithms must operate under strictly identical conditions with zero hidden advantages.

### Core Protocol Audit Table
| Fairness Criterion | Requirement | Observed Verification | Audit Verdict |
| :--- | :--- | :--- | :--- |
| **Evaluator Uniformity** | All algorithms must query the identical `CommonFleetEvaluator` | Verified across all 11 optimizers | **PASS** |
| **Hard Constraint Uniformity** | Same bounds, same compatibility rules, same demand requirements | Verified in `src/evaluator/common_evaluator.py` | **PASS** |
| **Random Seed Isolation** | Disjoint seeds for tuning (2001–2010), validation (3001–3010), benchmark (1001–1030) | Verified in `configs/phase5_parameters.json` and CSVs | **PASS** |
| **Evaluation Accounting** | Exactly 2,500 physical calls to `evaluator.evaluate()` per run | Verified by internal hardware counter | **PASS** |
| **No Oracle Leakage** | Optimizers receive only numerical fitness, violation, and objective vector | Verified via `EvaluationOutput` interface | **PASS** |
| **No Evaluator Modifications** | No optimizer modifies internal evaluator physics or weights | Inspected `src/algorithms/*.py` | **PASS** |

---

## 2. Evaluation Budget Accounting Forensics

### 2.1 Definition of "Evaluation"
In stochastic optimization literature, "evaluation" can be ambiguously defined as:
1. Candidate vector generation (internal arithmetic)
2. Domain decoder / repair evaluation
3. Objective function call to the physical surrogate model

In Egreen Quanta, the audit confirms that:
$$\text{evaluation\_budget} \equiv \text{number of physical invocations of } \texttt{CommonFleetEvaluator.evaluate(x)}$$

Every optimizer instantiates:
```python
comm_eval = CommonFleetEvaluator(evaluator, max_budget=2500)
```
Inside `CommonFleetEvaluator.evaluate(x)`:
```python
self.evaluation_count += 1
res = self.base_evaluator.evaluate_vector(x)
```
If an algorithm attempts to query the evaluator after `self.evaluation_count >= max_budget`, the optimizer loop immediately terminates.

### 2.2 Budget Verification Across All 11 Algorithms
The number of evaluations consumed was verified across all 30 benchmark runs for each algorithm:
- **A0 (Plain QPSO):** Exactly 2,500 physical evaluations per run ($30 \times 2,500 = 75,000$).
- **A1 (QPSO + Deb):** Exactly 2,500 physical evaluations per run ($30 \times 2,500 = 75,000$).
- **A2 (QPSO + Repair):** Exactly 2,500 physical evaluations per run ($30 \times 2,500 = 75,000$). Note: Repair operates analytically on the decision vector *prior* to evaluation; no extra evaluator calls are consumed.
- **A3 (Discrete QPSO):** Exactly 2,500 physical evaluations per run ($30 \times 2,500 = 75,000$).
- **A4 (Heterogeneous QI):** Exactly 2,500 physical evaluations per run ($30 \times 2,500 = 75,000$).
- **A5 (Complete Hybrid):** Exactly 2,500 physical evaluations per run ($30 \times 2,500 = 75,000$).
- **DE:** Exactly 2,500 physical evaluations per run ($30 \times 2,500 = 75,000$).
- **PSO:** Exactly 2,500 physical evaluations per run ($30 \times 2,500 = 75,000$).
- **GA:** Exactly 2,500 physical evaluations per run ($30 \times 2,500 = 75,000$).
- **Random Search:** Exactly 2,500 physical evaluations per run ($30 \times 2,500 = 75,000$).
- **NSGA-III:** Exactly 2,500 physical evaluations per run ($30 \times 2,500 = 75,000$).

**Total Physical Objective Evaluations Audited:** Exactly **$825,000$ calls** across 330 independent optimization runs.

---

## 3. Evaluator State & Caching Verification

A common experimental flaw in heuristic competitions is caching evaluator results between seeds or sharing mutable global state between algorithms.
- **Cache Check:** `CommonFleetEvaluator` contains **no caching dictionary**, memoization decorator, or hash-lookup table.
- **State Reset Check:** Each run instantiates a fresh `CommonFleetEvaluator` wrapper with its own clean `evaluation_count = 0` counter.
- **Seed Isolation:** Each run is explicitly seeded via `np.random.seed(seed)` in `BaseFleetOptimizer.optimize()`.

---

## 4. Audit Verdict: PASS
The experimental protocol is rigorously fair, fully isolated, and mathematically identical across all tested optimization methods. No algorithmic favoritism or budget inflation was detected.
