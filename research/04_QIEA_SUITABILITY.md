# 04 — QIEA SUITABILITY FOR HETEROGENEOUS FLEET
## RQ3: Can Quantum-Inspired Evolutionary Algorithms Handle Our Problem?

---

## 1. Our Problem's Constraint Breakdown

The SIH26138 heterogeneous fleet optimizer handles:

| Variable Type | # Variables | QIEA Suitability | Notes |
|:---|:---:|:---:|:---|
| **Speed** $s_v \in \mathbb{R}$ | V=6 | ⚠️ Indirect | Via Gray-code or amplitude rotation |
| **Fuel mode** $f_v \in \{1..4\}$ | 6 | ✅ Direct | Categorical probability vector |
| **Demand assignment** $d_{v,k} \in \{0,1\}$ | ~48 | ✅ Native | Binary Q-bit, native QIEA |
| **Shore power** $p_v \in \{0,1\}$ | 6 | ✅ Native | Binary Q-bit |
| **CII compliance** | Constraint | ✅ Filter | Feasibility rule during observation |
| **Capacity constraint** | Constraint | ✅ Repair | Post-observation repair operator |
| **Alternative fuels** | Objective | ✅ Via fuel mode | Cost/GHG table lookup |

---

## 2. Q-bit Representation for Fleet Variables

### 2.1 Binary Variables (Demand Assignment, Shore Power)

For a single binary variable $x \in \{0,1\}$ (e.g., $d_{v,k}$ or $p_v$):

$$Q^{(j)} = \begin{bmatrix} \alpha_j \\ \beta_j \end{bmatrix}, \quad |\alpha_j|^2 + |\beta_j|^2 = 1$$

Observation: $x_j = 1$ if $u < |\beta_j|^2$, else $x_j = 0$, where $u \sim U(0,1)$

**This is exactly what QIEA was designed for.** Each $d_{v,k}$ gets one Q-bit. The 48-dimensional assignment space is represented by 48 Q-bits. The superposition of Q-bit states maintains a rich probability distribution over all $2^{48}$ possible assignments, but only $O(P \cdot 48)$ evaluations are needed per generation.

### 2.2 Categorical Variables (Fuel Mode)

For fuel mode $f_v \in \{1, 2, 3, 4\}$ (HFO, LNG, Methanol, Bio-HFO):

**Extension to K-categorical Q-bit (categorical Q-vector):**

$$Q_{fuel,v} = \begin{bmatrix} p_1 & p_2 & p_3 & p_4 \end{bmatrix}, \quad \sum_{k=1}^{4} p_k = 1, \quad p_k \geq 0$$

Observation: Sample fuel mode from categorical distribution $\text{Cat}(p_1, p_2, p_3, p_4)$.

This is a **Dirichlet-distributed Q-vector**. Update is via:
$$p_k' = p_k + \eta \cdot \mathbb{1}[\hat{f}_{v,best} = k] - \lambda \cdot p_k$$

where $\hat{f}_{v,best}$ is the best observed fuel mode, $\eta$ is the learning rate, and $\lambda$ is a regularization term to prevent premature collapse.

This is equivalent to **cross-entropy minimization** toward the elite fuel allocation.

### 2.3 Continuous Variables (Speed)

Speed $s_v \in [v_{min}, v_{max}]$ is continuous. QIEA handles this via:

**Option A: Gray-code discretization.** Discretize speed into $B$-bit binary representation. With $B=8$, resolution is $\Delta s = (v_{max}-v_{min})/256 \approx 0.06$ knots. This is sufficient for operational purposes.

**Option B: Q-amplitude rotation for real values.** Interpret the Q-bit amplitude angle $\theta = \arctan(\beta/\alpha) \in [0, \pi/2]$ as a scaled real value: $s_v = v_{min} + (v_{max}-v_{min}) \cdot (2\theta/\pi)$.

**Option C (Hybrid):** Use QIEA for binary/categorical variables and QPSO for continuous speed variables in a coordinated update framework. This is our recommended architecture.

---

## 3. Constraint Handling in QIEA

### 3.1 Demand Partitioning via Conditional Observation

The one-hot assignment constraint $\sum_v d_{v,k} = 1$ can be enforced **during observation** (not post-hoc):

```
For each demand unit k:
  1. Compute normalized weights: w_v = |β_{v,k}|² for each vessel v
  2. Normalize: p_v = w_v / Σ_v w_v
  3. Sample: v* ~ Cat(p_1, ..., p_V)
  4. Set: d_{v*,k} = 1, d_{v,k} = 0 for v ≠ v*
```

This guarantees $\sum_v d_{v,k} = 1$ **by construction**. No repair operator needed. No penalty for this constraint. The partition constraint becomes part of the observation mechanism.

This is a **key advantage** over QPSO and DE, which must rely on post-hoc repair or penalty.

### 3.2 Capacity Constraint via Feasibility-First Selection

After observation, if vessel $v$ is overloaded ($\sum_k d_{v,k} w_k > C_v$):

Apply **Deb's constraint handling rule** (Deb 2000):
1. A feasible solution always beats an infeasible one
2. Between two infeasible solutions, the one with fewer violations wins
3. Between two feasible solutions, the one with better objective wins

This prevents Penalty Inversion without requiring any penalty parameter tuning.

### 3.3 CII Compliance as Hard Constraint

CII compliance can be enforced as:
$$\text{CII}(v, s_v, f_v) = \frac{\text{CO}_2(v, s_v, f_v)}{\text{transport\_work}(v)} \leq \text{CII}_{ref,v}$$

If violated during observation, the observation is rejected and the Q-bit update is biased away from the violating configuration:

$$\Delta\theta_{s_v} = \begin{cases} +\delta & \text{if } s_v > s_{CII,max}(v, f_v) \\ -\delta & \text{if } s_v < s_{CII,min}(v, f_v) \\ 0 & \text{otherwise} \end{cases}$$

This integrates regulatory compliance directly into the quantum-inspired search process.

---

## 4. Population Diversity in QIEA

QIEA maintains diversity through:
1. **Q-bit superposition**: early in optimization, $|\alpha|^2 \approx |\beta|^2 \approx 0.5$, allowing full binary exploration
2. **Catastrophic mutation**: with probability $p_m$, flip Q-bit to complement state. This is analogous to GA mutation but acts on probabilities, not single solutions.
3. **Migration**: in multi-population QIEA, periodic migration of Q-bit chromosomes across subpopulations prevents premature convergence.

QIEA's diversity properties are theoretically stronger than QPSO for binary/categorical problems because the Q-bit maintains a distribution over the entire feasible space until forced to collapse by evidence.

---

## 5. Convergence Properties

**Han & Kim (2002)** proved that QIEA converges to the global optimum with probability 1 under mild conditions:
1. Catastrophic mutation ensures ergodicity (every state is reachable)
2. Rotation gate ensures monotone improvement in expected Q-bit amplitude toward best known
3. Finite-population size introduces noise but the Markov chain is irreducible

**Practical convergence:** For problems of our scale (D~70 variables, V=6 vessels), QIEA typically converges within 500-1000 evaluations for binary/categorical subproblems.

---

## 6. QIEA Weaknesses (Honest Assessment)

| Weakness | Severity | Mitigation |
|:---|:---:|:---|
| Continuous variable handling is indirect | Medium | Hybrid with QPSO for speed |
| Rotation gate tuning is problem-dependent | Low | Standard rotation table from Han & Kim 2002 |
| Population size must be tuned | Low | Rule of thumb: 20-50 individuals for our problem scale |
| Convergence on real-valued objectives slower than DE | Medium | QPSO handles continuous dimensions |
| No velocity memory for speed updates | Medium | QPSO provides this natively |

**Conclusion:** QIEA is the appropriate primary framework for binary/categorical decision variables in SIH26138. Its weaknesses for continuous optimization are exactly covered by QPSO's strengths. This natural complementarity motivates the hybrid architecture.
