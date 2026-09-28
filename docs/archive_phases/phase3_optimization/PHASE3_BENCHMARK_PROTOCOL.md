# PHASE 3 BENCHMARK PROTOCOL
**Project:** SIH26138 — Egreen Quanta: Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization  
**Stage:** Optimization Metaheuristic Benchmarking & Fairness Protocol  
**Date:** 2026-09-12  
**Status:** BENCHMARK PROTOCOL LOCKED  

---

## 1. Scientific Principles of Fair Metaheuristic Benchmarking

Metaheuristic benchmarks in maritime optimization frequently suffer from methodological flaws:
1. Comparing algorithms with unequal function evaluation budgets.
2. Reporting results from a single favorable random seed.
3. Using wall-clock time as a primary comparison metric across mismatched implementations.
4. Suppressing runs where the proposed algorithm is outperformed.

In SIH26138, metaheuristic benchmarking adheres to the rigorous empirical guidelines of **Derrac et al. (2011)** and **Eiben & Jelasity (2002)**:
- **Evaluation Budget is the Gold Standard**: The primary resource budget is the number of candidate objective evaluations ($N_{\text{eval}}$).
- **Matched Seeds**: All algorithms execute on identical pseudorandom number generator (PRNG) seed sequences.
- **Hypothesis Falsification**: **QPSO MUST BE ALLOWED TO LOSE.** If canonical PSO, GA, or DE finds superior or identical solutions with lower variance, that result is recorded and reported without suppression.

---

## 2. Evaluation Budgets & Population Parameterizations

All algorithms are benchmarked under identical evaluation budgets:

$$\text{Total Evaluations } N_{\text{eval}} = \text{Swarm / Population Size } M \times \text{Generations } T = 50,000$$

### Parameter Settings for Fair Comparison:

| Algorithm Code | Method Name | Swarm/Pop Size $M$ | Iterations / Generations $T$ | Total Evaluations $N_{\text{eval}}$ | Hyperparameters |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `OPT-QPSO` | Quantum-Behaved PSO | 100 | 500 | 50,000 | $\beta_{\text{start}} = 1.0$, $\beta_{\text{end}} = 0.5$ (linear decay) |
| `OPT-PSO` | Canonical PSO | 100 | 500 | 50,000 | $w = 0.7298$, $c_1 = 1.49618$, $c_2 = 1.49618$ (Clerc constriction) |
| `OPT-GA` | Genetic Algorithm | 100 | 500 | 50,000 | Tournament size = 3, SBX $\eta_c = 15$, Poly Mutation $\eta_m = 20$, $p_c = 0.9$, $p_m = 0.1$ |
| `OPT-DE` | Differential Evolution | 100 | 500 | 50,000 | DE/rand/1/bin, $F = 0.8$, $CR = 0.9$ |
| `OPT-RS` | Uniform Random Search | N/A | N/A | 50,000 | Uniform independent random sampling across bounded space |

*Fast Test Tier*: For CI/CD automated regression testing, a proportional fast tier is defined with $M = 20, T = 50 \implies N_{\text{eval}} = 1,000$.

---

## 3. Seed Replication & Statistical Significance Testing

### 3.1 30-Seed Replicated Runs
Each algorithm is evaluated across **30 independent seeds**:
$$\mathcal{S} = \{42, 101, 202, 303, 404, 505, 606, 707, 808, 909, \dots, 2929\}$$
Minimum acceptable statistical threshold for exploratory runs is 10 seeds; primary scientific reporting requires all 30 seeds.

### 3.2 Paired Statistical Hypothesis Testing
For any paired comparison between algorithm $\mathcal{A}$ (e.g. QPSO) and baseline $\mathcal{B}$ (e.g. PSO) over $K = 30$ matched seeds:

1. **Difference Vector**:
   $$d_k = f_{\text{best}}(\mathcal{A}, \text{seed}_k) - f_{\text{best}}(\mathcal{B}, \text{seed}_k)$$
2. **Normality Test**: Shapiro-Wilk test on differences $\{d_k\}$. Because metaheuristic results are frequently non-Gaussian, parametric Student's $t$-tests are rejected in favor of non-parametric methods.
3. **Wilcoxon Signed-Rank Test**:
   - Ranked absolute differences $|d_k|$ with signs attached.
   - Test statistic $W = \min(W^+, W^-)$.
   - Significance threshold $\alpha = 0.05$.
4. **Effect Size (Rank-Biserial Correlation $r$)**:
   $$r = \frac{W^+ - W^-}{W^+ + W^-}$$
   Classification: $|r| < 0.1$ negligible, $0.1 \le |r| < 0.3$ small, $0.3 \le |r| < 0.5$ medium, $|r| \ge 0.5$ large.
5. **Hodges-Lehmann Estimator**:
   $$\tilde{\Delta}_{\text{HL}} = \text{median}\left\{ \frac{d_i + d_j}{2} \quad \middle| \quad 1 \le i \le j \le K \right\}$$
   Provides the non-parametric median difference with $95\%$ confidence interval.

---

## 4. Multi-Objective & Pareto Front Benchmarking Protocol

For multi-objective experiments (`EXP-OPT-04`):
1. **Nadir Reference Point Selection**:
   $$R_{\text{ref}} = \left[ 1.10 \times f_1^{\max}, 1.10 \times f_2^{\max}, 1.10 \times f_3^{\max}, 1.10 \times f_4^{\max}, 1.10 \times f_5^{\max} \right]^T$$
   Determined strictly from the union of all feasible evaluated points across all algorithms to ensure fair, non-truncated Hypervolume calculation.
2. **Hypervolume ($HV$) Calculation**:
   Normalized Lebesgue measure of objective space dominated by Pareto front $\mathcal{P}$ bounded by $R_{\text{ref}}$.
3. **Generational Distance ($GD$) and Inverted Generational Distance ($IGD$)**:
   Evaluated against reference front $\mathcal{P}^*_{\text{ref}}$, constructed by non-dominated sorting over the pool of all non-dominated solutions across all algorithms and seeds.

---

## 5. Standard Benchmark Scenario Suites

| Scenario ID | Name | Distance | Vessel Class | Weather State | Hard Deadline | Fuel Price | Carbon Price | Primary Goal |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| `SCEN-01` | North Sea Cruise Transit | 450 nm | Cruise (`CPS_Poseidon`) | Moderate ($H_s=2.0\text{ m}$) | 28.0 h | $620/t | $90/t | Fuel vs Delay Trade-off |
| `SCEN-02` | Atlantic Cruise Crossing | 1,200 nm | Cruise (`CPS_Poseidon`) | Rough ($H_s=3.8\text{ m}$) | 72.0 h | $620/t | $90/t | Weather Avoidance & FuelEU |
| `SCEN-03` | Offshore Supply Station | 120 nm | OSV (`OSS_Ceto`) | Calm ($H_s=1.0\text{ m}$) | 14.0 h | $680/t | $90/t | Transit vs DP Power Dispatch |
| `SCEN-04` | Multi-Fuel Decarbonization | 600 nm | Cruise (`CPS_Triton`) | Calm ($H_s=0.8\text{ m}$) | 36.0 h | Variable | $120/t | Green Alternative Fuel Selection |
| `SCEN-05` | Stress / Storm Scenario | 500 nm | Cruise (`CPS_Poseidon`) | Storm ($H_s=5.5\text{ m}$) | 32.0 h | $620/t | $90/t | Defensive Barrier Testing |

---

## 6. Execution & Reporting Requirements

Every benchmark script must save tabular data to `results/experiments/optimization/` with:
- Algorithm, Seed, Best Objective, Mean Objective, Std Objective, 95% CI.
- Number of Evaluations, Wall-Clock Runtime (s), In-Domain Feasibility Rate (%).
- Constraint violation counts (hard and soft).
- Wilcoxon $p$-values and effect sizes for all pairwise comparisons against QPSO.
