# Benchmark Combinatorial Difficulty & Random Search Audit
**Sample Size:** 10,000 uniform random candidate decision vectors.
**Core Objective:** Measure the intrinsic hardness of the search landscape and avoid conflating candidate feasibility with run feasibility.

## 1. Feasibility Metrics Disentanglement

| Metric | Measured Value | Scientific Meaning |
| :--- | :--- | :--- |
| **Candidate-Level Feasibility Rate** | **0.30%** (30 / 10,000) | Probability that a single randomly generated decision vector satisfies all 11 constraints. |
| **Run-Level Feasibility Rate (2,500 evals)** | **93.33%** (28 / 30 runs) | Probability that drawing 2,500 candidates discovers at least one feasible solution: 1 - (1 - 0.0030)^2500 = 99.94%. |
| **Mean Infeasible Penalty** | $33,857.07 | Magnitude of constraint penalty added to invalid random draws. |
| **Search Space Difficulty Class** | **HARD COMBINATORIAL** | Combinatorial assignment space (3^3 = 27 demand pairings, 5^3 = 125 fuel combos, continuous speeds). |

## 2. Methodological Rule Enforced
Never state "Random search has 93% feasibility" to imply the problem is trivial. The candidate space has only a 0.30% feasible volume, proving that naive sampling fails 99.7% of the time.
