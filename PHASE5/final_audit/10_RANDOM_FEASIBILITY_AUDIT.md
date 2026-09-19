# AUDIT #10: RANDOM SEARCH FEASIBILITY & COMBINATORIAL SAMPLING AUDIT
**Project:** SIH26138 — Egreen Quanta  
**Audit Section:** §14 Random Search Feasibility Forensics  
**Auditors:** Statistical Methods Auditor & Senior Optimization Research Scientist  
**Date:** September 15, 2026  

---

## 1. The Dual Meaning of Feasibility in Random Search

A frequent error in evolutionary computation and metaheuristic benchmarks is conflating **candidate-level sampling feasibility** with **run-level optimization success**:

1. **Candidate-Level Feasibility ($P_{\text{cand}}$):**  
   The probability that a single, uniformly drawn random decision vector $\mathbf{x} \sim U(\mathbf{x}_L, \mathbf{x}_U)$ satisfies all hard maritime operational constraints (demand coverage, engine-fuel compatibility, draft limits, and deadweight capacity).
2. **Run-Level Success Rate ($P_{\text{run}}$):**  
   The probability that an entire optimization run of $N_{\text{eval}} = 2,500$ independent random evaluations encounters **at least one** feasible solution.

---

## 2. Mathematical Verification & Binomial Analysis

### 2.1 Empirical Candidate-Level Sampling Rate
In the Phase 4 and Phase 5 empirical sampling tests:
$$\text{Feasible Candidates} = 30 \quad \text{out of} \quad 10,000 \text{ random draws}$$
$$P_{\text{cand}} = \frac{30}{10,000} = 0.0030 \quad (\mathbf{0.30\%})$$
This proves that the maritime heterogeneous fleet feasible region is **sparse**; an unguided draw has less than a one-in-three-hundred chance of being valid.

### 2.2 Theoretical Run-Level Success Probability
If an algorithm conducts $N = 2,500$ independent random draws, the probability that *none* are feasible is:
$$P(\text{all infeasible}) = (1 - P_{\text{cand}})^N = (1 - 0.0030)^{2500} = (0.9970)^{2500} \approx 0.000547$$
The theoretical probability of finding **at least one feasible candidate** in 2,500 evaluations is:
$$P(\text{at least one feasible}) = 1 - P(\text{all infeasible}) = 1 - 0.000547 = \mathbf{99.945\%}$$

### 2.3 Empirical Benchmark Observation (`Random.csv`)
- In `PHASE5/results/Random.csv`, **29 out of 30 independent runs** ($96.67\%$) discovered at least one feasible solution before evaluation 2,500.
- Average evaluation index where first feasible candidate appeared: **$375.8$ evaluations** (theoretically expected: $1 / 0.0030 \approx 333$ evaluations).
- Average candidate feasibility rate logged across all runs: **$0.30\%$**.

---

## 3. Mandatory Reporting Language & Juridical Standard

To prevent misleading the SIH evaluation jury, the project documentation shall strictly enforce the following language rules:

### Forbidden Statement:
❌ *"Random search is 96.67% feasible, showing the problem is trivial."*  
*(This falsely implies that 96.67% of the search space is feasible).*

### Mandatory Correct Statement:
✔ *"Individual random candidates have only a 0.30% probability of satisfying all constraints, demonstrating a sparse feasible region. However, across an evaluation budget of 2,500 random draws, 96.67% of runs discovered at least one feasible candidate, fully consistent with binomial probability theory ($1 - 0.997^{2500} = 99.95\%$)."*

---

## 4. Audit Verdict: PASS
The mathematical distinction is rigorously maintained, verified by probability theory, and correctly documented in the raw benchmark CSVs.
