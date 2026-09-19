# 10 — PROPOSED HYBRID QI-HFO ARCHITECTURE
## Hybrid Quantum-Inspired Heterogeneous Fleet Optimizer

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│           Hybrid QI-HFO Algorithm                       │
│                                                         │
│  ┌─────────────────────────┐   ┌───────────────────────┐│
│  │  QIEA Component         │   │  QPSO Component       ││
│  │  (Binary + Categorical) │   │  (Continuous Speed)   ││
│  │                         │   │                       ││
│  │  Q-bit: Shore Power     │   │  Quantum well:        ││
│  │  Q-vector: Fuel Mode    │◄──►  Speed per vessel     ││
│  │  Q-bit: Demand Assign   │   │  Contraction-expansion││
│  └─────────────────────────┘   └───────────────────────┘│
│                  │                         │             │
│                  └──────────┬──────────────┘             │
│                             ▼                            │
│               ┌─────────────────────────┐               │
│               │  Fitness Evaluator      │               │
│               │  - Fuel cost            │               │
│               │  - GHG intensity        │               │
│               │  - CII compliance       │               │
│               │  - FuelEU Maritime      │               │
│               │  - CVaR (weather)       │               │
│               │  - Assignment penalties │               │
│               └─────────────────────────┘               │
│                             │                            │
│               ┌─────────────▼─────────────┐             │
│               │  Selection & Update       │             │
│               │  QIEA: Deb's rule + Q-bit │             │
│               │  QPSO: Deb's rule + mbest │             │
│               └───────────────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Decision Variable Encoding

```
Solution Vector x = [
  # QIEA-controlled (discrete/categorical)
  d[v,k] for all v,k     → Q-bit binary (conditional observation)
  p[v] for all v          → Q-bit binary (standard)
  f[v] for all v          → Dirichlet-Q categorical
  
  # QPSO-controlled (continuous)
  s[v] for all v          → Quantum delta-well position
]
```

**Total dimensions:**
- QIEA: $V \cdot D + V + V = 6 \cdot 8 + 6 + 6 = 60$ Q-bits/Q-vectors
- QPSO: $V = 6$ continuous dimensions
- Total effective search space: enormous (manageable by probabilistic encoding)

---

## 3. Algorithm Pseudocode

```python
"""
Hybrid QI-HFO Pseudocode
Python-style for clarity; actual implementation will use optimized NumPy operations.
"""

def HybridQIHFO(
    n_pop: int = 40,           # Population size
    n_gen: int = 200,          # Generations
    n_vessels: int = 6,
    n_demand: int = 8,
    n_fuel_modes: int = 4,
    beta_initial: float = 1.0, # QPSO contraction-expansion
    beta_final: float = 0.5,
    eta: float = 0.05,         # QIEA learning rate
    lambda_reg: float = 0.01,  # Dirichlet regularization
    seeds: list = range(30),
) -> dict:

    # ────────────────────────────────────────────────────
    # INITIALIZATION
    # ────────────────────────────────────────────────────
    
    # QIEA: Initialize Q-bit matrices (binary)
    Q_demand = np.full((n_pop, n_vessels, n_demand), [1/√2, 1/√2])  # |α|²=|β|²=0.5
    Q_shore = np.full((n_pop, n_vessels), [1/√2, 1/√2])
    
    # QIEA: Initialize categorical Q-vectors (fuel mode)
    Q_fuel = np.full((n_pop, n_vessels, n_fuel_modes), 1/n_fuel_modes)  # Uniform
    
    # QPSO: Initialize speed positions
    X_speed = np.random.uniform(v_min, v_max, (n_pop, n_vessels))
    
    # Archive: track best feasible solutions
    gbest_speed = None
    gbest_discrete = None
    gbest_fitness = np.inf
    pbest_speed = X_speed.copy()
    pbest_discrete = None  # Will be set after first evaluation
    pbest_fitness = np.full(n_pop, np.inf)
    
    # ────────────────────────────────────────────────────
    # MAIN LOOP
    # ────────────────────────────────────────────────────
    for gen in range(n_gen):
        β = beta_initial - (beta_initial - beta_final) * gen / n_gen  # Linear decay
        
        for i in range(n_pop):
            # ────────────────────────────────────────────
            # STEP 1: QIEA OBSERVATION (categorical/binary)
            # ────────────────────────────────────────────
            
            # Demand assignment (conditional observation)
            d_observed = conditional_observe_demand(Q_demand[i], vessel_capacities)
            # Guarantees sum_v d[v,k] = 1 for all k by construction
            
            # Shore power (standard binary observation)
            p_observed = binary_observe(Q_shore[i])
            # Apply port capability filter: p_v = 0 if port not shore-capable
            p_observed = p_observed & port_shore_capable[vessel_route]
            
            # Fuel mode (categorical Dirichlet-Q observation)
            f_observed = categorical_observe(Q_fuel[i])
            # Apply fuel availability filter per port
            f_observed = apply_fuel_availability_filter(f_observed, vessel_routes)
            
            # ────────────────────────────────────────────
            # STEP 2: QPSO UPDATE (continuous speed)
            # ────────────────────────────────────────────
            
            if gbest_speed is not None:
                φ = np.random.uniform(0, 1, n_vessels)
                p_attractor = φ * pbest_speed[i] + (1 - φ) * gbest_speed
                mbest = np.mean(pbest_speed, axis=0)
                u = np.random.uniform(0, 1, n_vessels)
                sign = np.random.choice([-1, 1], n_vessels)
                X_speed[i] = p_attractor + sign * β * np.abs(mbest - X_speed[i]) * np.log(1/u)
            
            X_speed[i] = np.clip(X_speed[i], v_min, v_max)
            
            # ────────────────────────────────────────────
            # STEP 3: FITNESS EVALUATION
            # ────────────────────────────────────────────
            
            fitness, feasible, cii_ok, fueleu_ok = evaluate_fitness(
                speed=X_speed[i],
                fuel=f_observed,
                demand=d_observed,
                shore=p_observed,
                weather_scenarios=weather_scenarios,  # CVaR
            )
            
            # ────────────────────────────────────────────
            # STEP 4: DEBs FEASIBILITY-FIRST SELECTION
            # ────────────────────────────────────────────
            
            if deb_prefers(fitness, feasible, pbest_fitness[i], pbest_feasible[i]):
                pbest_speed[i] = X_speed[i].copy()
                pbest_discrete[i] = (d_observed, p_observed, f_observed)
                pbest_fitness[i] = fitness
                pbest_feasible[i] = feasible
            
            if deb_prefers(fitness, feasible, gbest_fitness, gbest_feasible):
                gbest_speed = X_speed[i].copy()
                gbest_discrete = (d_observed, p_observed, f_observed)
                gbest_fitness = fitness
                gbest_feasible = feasible
            
            # ────────────────────────────────────────────
            # STEP 5: QIEA Q-BIT UPDATE (rotation gate)
            # ────────────────────────────────────────────
            
            # Only update Q-bits when current solution dominated by best known
            best_d, best_p, best_f = gbest_discrete or pbest_discrete[i]
            
            # Update demand Q-bits
            for v in range(n_vessels):
                for k in range(n_demand):
                    Q_demand[i, v, k] = quantum_rotation(
                        Q_demand[i, v, k], d_observed[v,k], best_d[v,k]
                    )
            
            # Update shore power Q-bits
            for v in range(n_vessels):
                Q_shore[i, v] = quantum_rotation(
                    Q_shore[i, v], p_observed[v], best_p[v]
                )
            
            # Update fuel mode Dirichlet-Q
            for v in range(n_vessels):
                Q_fuel[i, v] = dirichlet_update(
                    Q_fuel[i, v], f_observed[v], best_f[v], eta, lambda_reg
                )
    
    return {
        'best_fitness': gbest_fitness,
        'best_feasible': gbest_feasible,
        'best_solution': (gbest_speed, gbest_discrete),
        'pbest_history': ...,  # For convergence analysis
    }
```

---

## 4. Key Functions

### 4.1 Conditional Demand Observation

```python
def conditional_observe_demand(Q_demand, vessel_capacities):
    """
    Guarantee sum_v d[v,k] = 1 for all k.
    """
    d = np.zeros((n_vessels, n_demand), dtype=int)
    for k in range(n_demand):
        # Probability of assigning demand k to vessel v
        probs = np.array([Q_demand[v, k, 1]**2 for v in range(n_vessels)])
        # Filter out vessels that cannot accommodate demand k
        mask = vessel_capacities >= demand_size[k]
        probs = probs * mask
        if probs.sum() == 0:
            probs = mask.astype(float)  # Uniform over capable vessels
        probs = probs / probs.sum()  # Normalize
        # Sample one vessel
        v_assigned = np.random.choice(n_vessels, p=probs)
        d[v_assigned, k] = 1
    return d
```

### 4.2 Dirichlet-Q Update (Categorical Fuel Mode)

```python
def dirichlet_update(q_fuel, f_observed, f_best, eta, lambda_reg):
    """
    Update categorical probability vector for fuel mode.
    """
    q_new = q_fuel.copy()
    q_new[f_best] += eta  # Increase probability of best observed fuel
    q_new -= lambda_reg * q_fuel  # Regularization: prevent collapse
    q_new = np.clip(q_new, 0.01, None)  # Minimum floor to preserve diversity
    q_new = q_new / q_new.sum()  # Re-normalize
    return q_new
```

### 4.3 Deb's Feasibility-First Rule

```python
def deb_prefers(f1, feasible1, f2, feasible2):
    """
    Return True if solution 1 is preferred over solution 2.
    """
    if feasible1 and feasible2:
        return f1 < f2
    elif feasible1 and not feasible2:
        return True  # Always prefer feasible
    elif not feasible1 and feasible2:
        return False
    else:
        return f1 < f2  # Both infeasible: prefer lower objective
```

---

## 5. Parameter Recommendations

| Parameter | Recommended Value | Justification |
|:---|:---:|:---|
| Population size ($n_{pop}$) | 40 | 20-40 is standard for QIEA at this problem scale |
| Generations ($n_{gen}$) | 250 | Matching Phase 4 budget: 40×250 = 10,000 evaluations |
| $\beta_{initial}$ | 1.0 | Standard QPSO; full exploration |
| $\beta_{final}$ | 0.5 | Standard QPSO; refined exploitation |
| QIEA learning rate ($\eta$) | 0.05 | Han & Kim (2002) recommendation |
| Dirichlet regularization ($\lambda$) | 0.01 | Prevents premature fuel mode collapse |
| Catastrophic mutation rate | 0.05 | Standard QIEA; preserves diversity |
| CVaR confidence level | 0.95 | Industry standard for maritime risk |
| Weather scenarios | 10 (fast) / 50 (precise) | Balance between accuracy and compute |

---

## 6. Computational Cost Analysis

For the 6-vessel, 8-demand, 4-fuel benchmark:
- QIEA observation: $O(V \cdot D + V + V \cdot K)$ per individual = $O(6 \cdot 8 + 6 + 6 \cdot 4) = 78$ operations
- QPSO update: $O(V)$ per individual = $O(6)$ operations
- Fitness evaluation: $O(S_{weather})$ per individual where $S_{weather}$ = weather scenarios
- Total per generation: $O(n_{pop} \cdot (78 + 6 + S_{weather}))$
- Total over all generations: $n_{gen} \cdot n_{pop} \cdot (84 + S_{weather})$

With $n_{gen}=250$, $n_{pop}=40$, $S_{weather}=10$:
Total operations: $250 \times 40 \times (84+10) = 940{,}000$

This is comparable to Phase 4's budget of $200 \times 50 = 10{,}000$ fitness evaluations (note: fitness evaluation dominates).

---

## 7. What This Architecture Is NOT

- It is NOT a novel algorithm in the sense of introducing new quantum-mechanical primitives
- It is NOT claiming quantum speedup — it runs on classical hardware
- It is NOT claiming that hybrid QI-HFO will outperform DE — that is an empirical question
- It IS a principled combination of existing quantum-inspired components that addresses a specific representational deficiency identified in Phase 4.1
