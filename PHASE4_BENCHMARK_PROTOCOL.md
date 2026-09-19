# PHASE 4 BENCHMARK PROTOCOL
## Egreen Quanta / SIH26138: Heterogeneous Fleet, Uncertainty-Aware & Scientifically Defensible Optimization

**Provenance**: `REAL_TELEMETRY_CALIBRATED` / `SYNTHETIC_OPERATIONAL_SCENARIO`  
**Repository**: `sih26138_platform`  
**Date**: September 2026  

---

## 1. Scientific Objective & Primary Hypotheses

The primary scientific objective of Phase 4 is to determine whether quantum-inspired metaheuristics (QPSO) exhibit statistically and practically meaningful computational advantages over established classical optimization algorithms (DE, PSO, GA, and Random Search) under strictly equal computational evaluation budgets on a hard, heterogeneous, mixed-integer green fleet optimization benchmark.

### Formal Hypothesis Testing:
- **Null Hypothesis ($H_0$)**: There is no statistically significant or practically meaningful difference in solution quality between QPSO and classical baselines under equal function evaluations on the Level 4 heterogeneous fleet benchmark ($\Delta J = 0$, $p \ge 0.05$, or $|\text{Improvement}| < 1.0\%$).
- **Alternative Hypothesis ($H_1$)**: QPSO achieves statistically superior and practically meaningful reductions in the robust master objective compared to classical baselines under equal evaluation budgets ($p < 0.05$ and $\text{Improvement} \ge 1.0\%$).

*Scientific Rule: The benchmark is strictly unmanipulated. Equivalence or negative results are fully preserved and defended.*

---

## 2. Fairness & Standardization Protocol

To ensure unimpeachable scientific validity, every optimization algorithm is subjected to an identical evaluation contract:

| Benchmark Dimension | Protocol Specification | Verification Method |
| :--- | :--- | :--- |
| **Objective Function** | Master scalar fitness $J_{\text{total}}$ (`Phase4FleetEvaluator`) | Identical Python callable passed to all optimizers |
| **Search Domain Bounds** | $D = 18$ bounded hypercube $[\mathbf{x}_l, \mathbf{x}_u]$ | Single canonical `get_bounds()` source |
| **Evaluation Budget** | Strictly **2,500 objective function evaluations** per run | Hard evaluation counter cap in each optimizer wrapper |
| **Primary Metric** | Objective evaluations used ($N_{\text{evals}}$), **not** iterations | Iteration count normalized by population size |
| **Seed Sequence** | 30 matched random seeds: $s \in [1001, 1030]$ | Fixed seed set passed identically to all algorithms |
| **Solution Decoding** | Canonical discrete/continuous mapper (`decode_fleet_vector`) | Centralized decoding prior to physics evaluation |
| **Constraint Barrier** | Identical penalty formulas for collisions and out-of-domain states | Shared defensive barrier engine |
| **Hardware Platform** | Single local workstation (20 CPU cores, identical RAM/OS) | Hardware metadata logged in manifest |

---

## 3. Evaluated Optimization Algorithms

1. **QPSO (Quantum-Behaved Particle Swarm Optimization)**:
   - Physics-inspired quantum delta-potential well dynamics (Sun et al. 2004).
   - Classical implementation running strictly on CPU cores (no QPU, no quantum computing).
   - Parameters: $N_{\text{particles}} = 50$, $T_{\text{max}} = 50$, $\beta_{\text{start}} = 1.0 \to \beta_{\text{end}} = 0.5$.
2. **DE (Differential Evolution)**:
   - Standard DE/rand/1/bin with binomial crossover.
   - Parameters: $N_{\text{pop}} = 50$, $F_{\text{mut}} = 0.8$, $CR = 0.9$.
3. **PSO (Canonical Particle Swarm Optimization)**:
   - Inertia weight velocity update with cognitive and social attractors.
   - Parameters: $N_{\text{particles}} = 50$, $w = 0.7 \to 0.4$, $c_1 = 1.5, c_2 = 1.5$.
4. **GA (Genetic Algorithm)**:
   - Real-coded tournament selection, simulated binary crossover (SBX), and polynomial mutation.
   - Parameters: $N_{\text{pop}} = 50$, $p_c = 0.9, p_m = 0.05, \eta_c = 20, \eta_m = 20$.
5. **Random Search Baseline**:
   - Uniform pseudo-random sampling over bounded continuous hypercube $[\mathbf{x}_l, \mathbf{x}_u]$ with $N = 2,500$.

---

## 4. Rigorous Statistical Testing Protocol

To eliminate known statistical artifacts (such as the zero-difference Wilcoxon anomaly identified in Phase 3.2):

### 4.1 Numerical Zero-Tolerance Thresholding
Any paired objective difference $|J_{\text{QPSO}, s} - J_{\text{baseline}, s}| \le 10^{-5}$ is treated as an exact numerical tie ($\Delta J = 0.0$). Floating-point discretization noise is strictly prohibited from manufacturing artificial rank differences.

### 4.2 Absolute Wilcoxon Applicability Rule
If all paired differences across the 30 seeds evaluate to zero ($n_{\text{nonzero}} = 0$):
$$\text{Wilcoxon Result} = \text{NOT APPLICABLE (Status: ALL TIES)}$$
$$p\text{-value} = 1.0, \quad \text{Statistic} = \text{NaN}, \quad \text{Is Significant} = \text{False}$$
No $p$-value is manufactured when non-zero ranks do not exist.

### 4.3 Multi-Method Statistical Battery
For each pairwise comparison (QPSO vs DE, QPSO vs PSO, QPSO vs GA, QPSO vs Random):
1. **Wilcoxon Signed-Rank Test** (two-sided, zero-method="wilcox").
2. **Permutation Test**: 100,000 exact sign-flip Monte Carlo resamples.
3. **Hodges-Lehmann Estimator**: Median of all pairwise Walsh averages $\frac{D_i + D_j}{2}$.
4. **Bootstrap 95% Confidence Interval**: 10,000 bootstrap replicates of mean difference.
5. **Holm-Bonferroni FWER Correction**: Multi-hypothesis correction across all 4 pairwise comparisons.
6. **Separation of Statistical vs Practical Significance**:
   $$\text{Relative Improvement (\%)} = 100 \times \frac{\bar{J}_{\text{baseline}} - \bar{J}_{\text{QPSO}}}{\bar{J}_{\text{baseline}}}$$
   An improvement is classified as *Practically Meaningful* only if $|\Delta J| \ge 1.0\%$ AND $p < 0.05$. Improvements $< 1.0\%$ are classified as *Negligible or Tie* regardless of $p$-value.
