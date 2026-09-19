# 03 — QPSO FORENSIC ANALYSIS: MATHEMATICAL ROOT-CAUSE
## Why QPSO Failed on Heterogeneous Fleet Optimization

---

## RQ2: Why does QPSO struggle with the heterogeneous fleet formulation?

This document provides the mathematical root-cause analysis for the 13.33% QPSO infeasibility rate (4 failed seeds out of 30) in Phase 4.

---

## 1. The SIH26138 Decision Variable Structure

Our fleet optimization problem has a **heterogeneous decision space**:

$$\mathbf{x} = \underbrace{(s_1, s_2, \ldots, s_V)}_{\text{speed: continuous, }\mathbb{R}^V} \oplus \underbrace{(f_1, f_2, \ldots, f_V)}_{\text{fuel: categorical, }\mathbb{Z}_K^V} \oplus \underbrace{(d_1, d_2, \ldots, d_V)}_{\text{demand: binary-assignment, }\{0,1\}^{V \times D}} \oplus \underbrace{(p_1, \ldots, p_V)}_{\text{shore: binary, }\{0,1\}^V}$$

- **Speed**: $s_v \in [v_{min}, v_{max}]$ — continuous, range typically [10, 25] knots
- **Fuel mode**: $f_v \in \{1, \ldots, K\}$ — categorical, $K=4$ modes (HFO, LNG, Methanol, Bio-HFO)
- **Demand assignment**: $d_{v,k} \in \{0, 1\}$ — binary, demand unit $k$ assigned to vessel $v$
- **Shore power**: $p_v \in \{0, 1\}$ — binary, shore power connection at port

A feasible solution must satisfy:
1. Each demand unit is assigned to exactly one vessel: $\sum_v d_{v,k} = 1 \;\forall k$
2. Vessel capacity not exceeded: $\sum_k d_{v,k} \cdot w_k \leq C_v \;\forall v$
3. Shore power only if port-capable: $p_v \leq \text{portcap}_v$
4. Fuel mode consistent with vessel equipment: $f_v \in \mathcal{F}_v$

---

## 2. How QPSO Encodes This (The Representation Defect)

Our QPSO implementation encodes the full decision vector in $\mathbb{R}^D$ where:
- $D = V + V + V \cdot D_{demand} + V = V(3 + D_{demand})$
- Categorical fuel mode: real-valued position in $[1, K]$, rounded to nearest integer
- Demand assignment: real-valued positions in $[0, 1]$, rounded to nearest binary
- Shore power: real-valued positions in $[0, 1]$, rounded to nearest binary

### 2.1 The Flat Gradient Problem for Categorical Variables

For a categorical variable $f_v$ with $K=4$ options, the QPSO position update is:
$$f_v^{(t+1)} = p_{f_v} \pm \beta(t) \cdot |mbest_{f_v} - f_v^{(t)}| \cdot \ln(1/u)$$

After rounding to $\{1,2,3,4\}$, the fitness landscape in $f_v$-space has a step-function structure:

$$J(\ldots, f_v, \ldots) = \begin{cases} J_1 & \text{if } f_v^{(raw)} \in [1.0, 1.5) \\ J_2 & \text{if } f_v^{(raw)} \in [1.5, 2.5) \\ J_3 & \text{if } f_v^{(raw)} \in [2.5, 3.5) \\ J_4 & \text{if } f_v^{(raw)} \in [3.5, 4.0] \end{cases}$$

**Gradient within each interval is zero**. The quantum-well attractor $p_{f_v}$ can float freely within $[1.5, 2.5)$ without any fitness signal distinguishing positions. This causes:
1. **Plateau stagnation**: particles accumulate in the interior of a categorical "bin"
2. **False exploration**: the swarm appears to explore but receives no signal to cross category boundaries
3. **Swarm collapse**: $mbest_{f_v}$ converges to the arithmetic mean of all personal bests — which may be a non-integer, non-representable value

### 2.2 The Assignment Constraint Collapse

For demand assignment variables $d_{v,k}$, constraint (1) requires $\sum_v d_{v,k} = 1$. The QPSO update does not enforce this:

$$d_{v,k}^{(t+1)} = \text{round}\left(p_{d_{v,k}} \pm \beta(t) \cdot |mbest_{d_{v,k}} - d_{v,k}^{(t)}| \cdot \ln(1/u)\right)$$

After rounding, it is possible that $\sum_v d_{v,k} \in \{0, 2, 3, \ldots\}$ for some demand unit $k$. QPSO has no mechanism to enforce the assignment partition constraint during update.

**This is the primary source of infeasibility in failed seeds.**

The penalty function applies:
$$F_{penalty} = P_{hard} \cdot \mathbb{1}[\text{demand violated}], \quad P_{hard} = \$50{,}000$$

However, when the swarm finds a local optimum with violated assignments where soft penalties total $J_{soft} \approx \$109{,}000$ for infeasible configurations (delay + overcapacity), the infeasible solution with penalty yields:

$$F_{infeasible} = \underbrace{J_{operational}^{low}}_{\text{low cost (bad assignment achieves low reported cost)}} + P_{hard}$$

If $J_{operational}^{low} + P_{hard} < J_{feasible}^{real}$, the infeasible configuration is **preferred by the fitness function**. This is **Penalty Inversion**.

### 2.3 Quantifying Penalty Inversion (Phase 4.1 Audit Result)

From `PHASE4_1_CLAIM_LEDGER.yaml` (Claim B — CONFIRMED):

| Condition | Value |
|:---|:---|
| Hard penalty magnitude | $\$50,000$ |
| Mean soft-penalty in failed seeds | $\$109,447$ |
| Minimum feasible cost (failed seeds) | $\$61,200$ |
| Effective penalty gap | $P_{hard} - J_{soft,min} = -\$59,447$ |
| Conclusion | Penalty Inversion confirmed |

The swarm in failed seeds found configurations where:
$$J_{operational, infeasible} + P_{hard} < J_{operational, feasible, min}$$

This caused the attractor to lock onto infeasible configurations.

---

## 3. Differential Evolution — Why It Succeeds

DE's mutation mechanism:
$$v_i = x_{r1} + F \cdot (x_{r2} - x_{r3})$$
$$u_i^j = \begin{cases} v_i^j & \text{if } r_j < CR \text{ or } j = j_{rand} \\ x_i^j & \text{otherwise} \end{cases}$$

For binary/categorical variables, DE uses coordinate-wise crossover:
- Each dimension is independently crossed — if $j_{rand}$ falls on a categorical dimension, the mutation operates on that dimension specifically
- The diversity of the trial vector is guaranteed by the three distinct parent requirement
- DE inherently maintains sufficient **heterozygosity** to escape local optima in categorical dimensions

DE achieves 100% feasibility because:
1. The crossover operation natively generates diverse categorical combinations
2. The population maintains three distinct solutions per update, preventing swarm collapse
3. DE's selection is purely greedy (greedy replacement), meaning infeasible solutions are rejected quickly

**This is a structural difference, not a QPSO weakness per se.** It is a consequence of QPSO's continuous ancestry.

---

## 4. Mathematical Summary of QPSO Failure Modes

| Failure Mode | Mathematical Cause | Evidence |
|:---|:---|:---|
| **M1: Categorical Plateau Stagnation** | Zero fitness gradient within categorical "bin" $[k-0.5, k+0.5)$ | Swarm position histograms (Phase 4.1) |
| **M2: Assignment Constraint Violation** | No partition enforcement in position update; QPSO generates $\sum_v d_{v,k} \neq 1$ | Infeasibility CSV (Phase 4.1) |
| **M3: Penalty Inversion** | $P_{hard} = \$50k < J_{soft,min} = \$61.2k$ in failure region | Claim Ledger, Claim B |
| **M4: Swarm Collapse** | $mbest$ converges to arithmetic mean of infeasible positions, reinforcing M1–M3 | Diversity trace (Phase 4.1) |

---

## 5. What a Corrected QPSO Would Require

To fix QPSO for this problem without a major representational change:

1. **Repair Operator** (post-update): for each demand unit $k$, if $\sum_v d_{v,k} \neq 1$, apply greedy assignment to the highest-probability vessel. Cost: $O(V \cdot D_{demand})$ per particle per iteration.

2. **Scaled Penalty** (constraint violation scaling): Replace $P_{hard}$ with dynamic scaling: $P_{hard}(t) = \max(J_{soft}^{best}(t), P_{base}) \cdot (1 + n_{violated})$ where $n_{violated}$ is the number of violated constraints. This eliminates Penalty Inversion by ensuring $P_{hard} > J_{soft}$ at all times.

3. **Feasibility-First Selection Rule** (Deb's rule): When comparing any two solutions, prefer feasible over infeasible regardless of objective value. Only compare objective values when both are feasible.

4. **Categorical Mutation Operator**: When a particle's categorical variable has not changed for $T_{stag}$ iterations, apply a random jump to a different category. Prevents categorical plateau stagnation.

**Note:** These fixes are well-described in literature (Deb 2000 for feasibility rules; multiple PSO constraint handling papers 2018–2024). They do not require a new algorithm design. They constitute **implementation corrections** to the existing QPSO.

The question of whether a hybrid representation (QIEA for categorical + QPSO for continuous) offers a more principled solution is addressed in Section 11 (Research Gap Analysis).
