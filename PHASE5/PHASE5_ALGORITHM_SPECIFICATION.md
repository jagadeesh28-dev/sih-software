# Phase 5 Algorithm Specification: Hybrid QI-HFO and A0–A5 Suite
## SIH26138 — Egreen Quanta

---

## 1. Algorithm Overview

This document provides complete, line-by-line mathematical specifications and pseudocode for all algorithms evaluated in the Phase 5 benchmark suite:
- **A0**: Plain Quantum-Behaved Particle Swarm Optimization (QPSO)
- **A1**: QPSO + Deb's Feasibility-First Constraint Handling
- **A2**: QPSO + Principled Decoder / Repair Mechanism
- **A3**: QPSO + Discrete Operators + Diversity Preservation
- **A4**: Heterogeneous Q-bit (QIEA) + Continuous QPSO (Penalty-Only)
- **A5**: Complete Hybrid QI-HFO (Full Framework)

---

## 2. Mathematical Update Equations

### 2.1 QIEA Quantum-Bit Mechanics (Discrete Space)

#### 2.1.1 Binary Q-Bit
A 2-state quantum bit represents a linear superposition:
$$|\psi\rangle = \alpha |0\rangle + \beta |1\rangle = \cos(\theta)|0\rangle + \sin(\theta)|1\rangle$$
Normalization is strictly preserved:
$$|\alpha|^2 + |\beta|^2 = \cos^2(\theta) + \sin^2(\theta) = 1$$
Measurement in the computational basis $\{|0\rangle, |1\rangle\}$ yields bit $b \in \{0, 1\}$:
$$b = \begin{cases} 1 & \text{if } u < \sin^2(\theta), \quad u \sim U(0, 1) \\ 0 & \text{otherwise} \end{cases}$$
Unitary quantum rotation gate:
$$R(\Delta\theta) = \begin{bmatrix} \cos(\Delta\theta) & -\sin(\Delta\theta) \\ \sin(\Delta\theta) & \cos(\Delta\theta) \end{bmatrix}$$
$$\begin{bmatrix} \alpha(t+1) \\ \beta(t+1) \end{bmatrix} = R(\Delta\theta) \begin{bmatrix} \alpha(t) \\ \beta(t) \end{bmatrix} \implies \theta(t+1) = \theta(t) + \Delta\theta$$
where the rotation angle $\Delta\theta = s(\alpha, \beta) \cdot \Delta\theta_0$, with magnitude $\Delta\theta_0 = 0.05\pi$ determined during the independent tuning phase.

#### 2.1.2 Dirichlet-Q Categorical Vector
For decisions with $K$ discrete alternatives (such as $K=5$ fuel modes), the categorical probability vector $\mathbf{q} \in \Delta^{K-1}$ satisfies $\sum_{k=0}^{K-1} q_k = 1$ and $q_k \ge \epsilon > 0$.
Given target/best category $k^*$:
$$q_{k^*}(t+1) = q_{k^*}(t) + \eta$$
$$q_k(t+1) = q_k(t) - \lambda_{\text{reg}} \cdot q_k(t), \quad \forall k \ne k^*$$
followed by projection: $q_k \leftarrow \max(q_k, \epsilon)$, and re-normalization: $\mathbf{q} \leftarrow \mathbf{q} / \sum_k q_k$.

#### 2.1.3 Conditional Demand Observation
To guarantee that $\sum_{v=1}^V d_{v,k} = 1$ without demand collisions:
```python
def conditional_observe_demand(thetas, compatibility_matrix):
    probs = np.sin(thetas)**2
    assigned_vessels = set()
    vessel_assignments = np.zeros(V, dtype=int)
    for k in range(K):
        p_k = probs[:, k].copy() * compatibility_matrix[:, k]
        for v in assigned_vessels:
            p_k[v] = 0.0
        p_norm = p_k / np.sum(p_k)
        chosen_v = sample_categorical(p_norm)
        vessel_assignments[chosen_v] = k + 1
        assigned_vessels.add(chosen_v)
    return vessel_assignments
```

---

### 2.2 QPSO Continuous Mechanics (Speed & Cargo Space)

Continuous operational variables (speed $s_v$ and cargo payload $m_v$) are governed by the quantum delta-potential well model:
1. **Mean Best Attractor**:
   $$\mathbf{m}_{\text{best}}(t) = \frac{1}{M} \sum_{i=1}^M \mathbf{p}_{\text{best},i}(t)$$
2. **Local Stochastic Attractor**:
   $$\mathbf{p}_{i,d}(t) = \phi_d \cdot p_{\text{best},i,d}(t) + (1 - \phi_d) \cdot g_{\text{best},d}(t), \quad \phi_d \sim U(0, 1)$$
3. **Contraction-Expansion Coefficient**:
   $$\beta(t) = \beta_{\text{start}} - (\beta_{\text{start}} - \beta_{\text{end}}) \frac{t}{T_{\max}}$$
   with $\beta_{\text{start}} = 0.9, \beta_{\text{end}} = 0.4$ (frozen via tuning).
4. **Position Update**:
   $$x_{i,d}(t+1) = p_{i,d}(t) \pm \beta(t) \cdot |m_{\text{best},d}(t) - x_{i,d}(t)| \cdot \ln\left(\frac{1}{u}\right), \quad u \sim U(0, 1)$$

---

## 3. Complete Pseudocode: A5 Complete Hybrid QI-HFO

```
Algorithm: A5 Complete Hybrid QI-HFO
Input: Evaluator E, Bounds [xl, xu], Population M=50, Budget B=2500, Seed s
Output: Best Solution gbest, Multi-Objective Pareto Archive A

1.  Initialize pseudo-random generator with seed s.
2.  Initialize Q-bit matrices:
    - Shore power Q-bits: theta_shore[i, v] = pi/4
    - Fuel Dirichlet-Q vectors: q_fuel[i, v, k] = 1/5
    - Demand amplitude matrix: theta_demand[i, v, k] = pi/4
3.  Initialize continuous positions X_speed, X_cargo uniformly in [xl, xu].
4.  For each particle i in 1..M:
        Observe discrete variables via Q-bits.
        Combine with continuous variables into candidate X[i].
        Apply FleetSolutionRepairer to X[i].
        Evaluate: out[i] = E.evaluate(X[i]).
        P[i] = X[i], P_out[i] = out[i].
        If out[i].is_feasible:
            Add out[i] to Pareto Archive A.
5.  Select initial gbest = argmin_Deb(P_out).
6.  While E.evaluation_count < B:
        Update beta(t) linearly from 0.9 to 0.4.
        Compute mbest = mean(P, axis=0).
        For each particle i in 1..M:
            If E.evaluation_count >= B: break
            
            // Tier 1: Quantum discrete observation
            demands = ConditionalDemandObservation(theta_demand[i])
            fuels   = MeasureDirichletQ(q_fuel[i])
            shores  = MeasureQBit(theta_shore[i])
            
            // Tier 2: QPSO continuous update
            p_local = phi * P[i] + (1 - phi) * gbest
            X[i] = p_local +/- beta * |mbest - X[i]| * ln(1/u)
            
            // Tier 3: Principled Repair
            X[i] = FleetSolutionRepairer.repair(X[i])
            
            // Tier 4: Common Evaluation
            out = E.evaluate(X[i])
            If out.is_feasible:
                Update Pareto Archive A with out.objectives.
                
            // Tier 5: Deb's Feasibility-First Selection
            If DebPrefers(out, P_out[i]):
                P[i] = X[i], P_out[i] = out
                // Unitary quantum rotation toward improved solution
                Rotate(theta_demand[i], demands)
                Rotate(q_fuel[i], fuels)
                Rotate(theta_shore[i], shores)
                
                If DebPrefers(out, gbest_out):
                    gbest = X[i], gbest_out = out
                    
7.  Prune Pareto Archive A using non-dominated sorting.
8.  Compute 2D Hypervolume on non-dominated set.
9.  Return gbest, gbest_out, A, and diagnostics.
```
