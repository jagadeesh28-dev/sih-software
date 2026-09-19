# Benchmark Integrity Repair & Disconfirmation Audit
**Standard:** IEEE Transactions on Evolutionary Computation & ACM Reproducibility Protocol
**Date:** September 18, 2026
**Lead Auditor:** Senior Optimization Research Engineer, Scientific Auditor & Hostile Reviewer

## 1. Contradictions Found & Root Cause Analysis

### Contradiction 1: Random Search Feasibility (0.30% vs. 93.33%)
- **Symptom:** Historical reports stated both "Random search has 93.3% feasibility" and "Random search has 0.30% feasibility".
- **Root Cause:** Conflation of candidate-level feasibility with run-level success. Candidate-level feasibility is the probability that a single uniformly drawn vector satisfies all 11 constraints ($p = 0.00300 = 0.30\%$). Run-level feasibility is the probability that an algorithm drawing 2,500 samples finds at least one feasible candidate ($1 - (1 - 0.0030)^{2500} = 99.94\%$; observed in 28/30 runs = $93.33\%$).
- **Resolution:** Explicitly decoupled in `results/raw/final_benchmark_master.csv`. The search space has only a $0.30\%$ feasible volume, proving the problem is hard combinatorial.

### Contradiction 2: NSGA-III Hypervolume Crippling (+64.0% Artificial Advantage)
- **Symptom:** Historical benchmarks claimed A5 Hybrid QI achieved a +64.0% Hypervolume advantage over NSGA-III ($247.11 	imes 10^6$ vs $150.67 	imes 10^6$).
- **Root Cause:** Severe experimental bias. A5 was wrapped with deterministic C0 Hungarian repair, while NSGA-III was denied repair and evaluated raw offspring. NSGA-III experienced an 80% feasibility failure rate and could not populate the Pareto archive.
- **Resolution:** Tested Fair NSGA-III with identical C0 Hungarian repair and Deb comparator across all 30 matched seeds. Fair NSGA-III achieved **100.0% feasibility** and **$247.07 	imes 10^6$ Hypervolume** ($p = 0.6089$ vs A5). **A5 has zero statistically significant Hypervolume advantage over classical NSGA-III under fair conditions.**

### Contradiction 3: DE Feasibility & Penalized Fitness
- **Symptom:** Classical DE was reported with a high mean penalized fitness ($3,976.19$) despite a median of $4.13$ and $100\%$ feasibility.
- **Root Cause:** Standard DE was run with additive penalties and without Hungarian repair, incurring soft arrival delay penalties on 5 out of 30 seeds.
- **Resolution:** Running Fair MODE with C0 repair and Deb comparator yields a mean physical fitness of **$3.3936$** ($p = 1.02 	imes 10^{-7}$ strictly superior to A5's $3.4483$) and a runtime of **$6.19	ext{ s}$** (faster than A5's $7.51	ext{ s}$).

### Contradiction 4: Scaling Complexity Claims ("Sub-Linear" Exponent)
- **Symptom:** Empirical scaling from $D=18$ to $D=600$ was termed "sub-linear algorithmic complexity" because fitted exponent $b < 1.0$.
- **Root Cause:** Exponent $b = 0.9257$ for A5 has a 95% confidence interval of `[0.8113, 1.0401]`, which includes linear scaling ($b = 1.0$). Furthermore, theoretical non-dominated sorting is $O(M \cdot N^2)$.
- **Resolution:** Formally retracted "sub-linear complexity". Described as empirical wall-clock scaling on classical multi-core CPUs.

## 2. Reconstructed Causal Ablation Chain (A0 to A6)

| Stage | Name | Feasibility | Physical Obj | Hypervolume ($10^6$) | Diversity ($D$) | Runtime (s) | Isolated Causal Mechanism |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A0** | Plain QPSO | 80.00% | 202.67 | 0.00 | 176.23 | 1.80s | Baseline continuous QPSO with static additive penalty. |
| **A1** | A0 + Deb | **100.00%** | **3.35** | 0.00 | 171.19 | 2.32s | **Deb's feasibility-first rule eliminates penalty inversion.** |
| **A2** | A1 + Repair | 100.00% | 3.39 | 0.00 | **5.75** | 4.96s | Deterministic repair guarantees zero collisions; collapses diversity. |
| **A3** | A2 + Archive | 100.00% | 3.39 | 245.80 | 5.75 | 5.20s | Multi-objective non-dominated tracking. |
| **A4** | Discrete + QPSO| 86.67% | 136.27 | 0.00 | 168.49 | 3.26s | Classical discrete rounding without repair causes boundary drift. |
| **A5** | Q-bit + QPSO | 100.00% | 3.45 | **247.11** | **189.54** | 7.51s | **Q-bits maintain high entropy ($D=189.54$) under repair.** |
| **A6** | Q-bit + DE | 100.00% | **3.39** | 246.78 | **224.10** | **6.19s** | **Classical DE provides superior continuous search over QPSO.** |

## 3. Transition Deltas & Rigorous Causal Analysis

| Transition | $\Delta$ Feasibility | $\Delta$ Physical Obj | $\Delta$ Hypervolume | $\Delta$ Diversity | $\Delta$ Runtime | Causal Finding |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A0 -> A1** | **+20.00%** | **-199.32** | 0.00 | -5.04 | +0.52s | **Deb's rule is 100% responsible for feasibility restoration.** |
| **A1 -> A2** | 0.00% | +0.04 | 0.00 | **-165.45** | +2.65s | Repair prevents duplicate demands but collapses swarm diversity. |
| **A2 -> A3** | 0.00% | 0.00 | **+245.80M** | 0.00 | +0.24s | Pareto archive enables trade-off tracking without changing search. |
| **A3 -> A4** | **-13.33%** | +132.88 | -245.80M | +162.74 | -1.95s | Removing repair causes categorical collision deadlock. |
| **A4 -> A5** | **+13.33%** | -132.82 | **+247.11M** | +21.05 | +4.26s | Q-bits preserve diversity ($D=189.54$) while repair ensures validity. |
| **A5 -> A6** | 0.00% | **-0.06** | -0.33M | **+34.57** | **-1.32s** | **Classical DE outperforms QPSO on fuel and runtime.** |
