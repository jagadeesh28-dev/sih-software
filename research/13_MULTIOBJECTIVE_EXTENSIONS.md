# 13 — MULTI-OBJECTIVE EXTENSIONS
## RQ18: How to Handle Multi-Objective Optimization?

---

## 1. Objective Structure of SIH26138

The SIH26138 problem has multiple competing objectives:

| Objective | Symbol | Unit | Direction |
|:---|:---|:---:|:---|
| Total operational cost | $J_{cost}$ | USD | Minimize |
| Fleet GHG intensity | $J_{GHG}$ | gCO₂eq/MJ | Minimize |
| Schedule reliability (delay) | $J_{delay}$ | hours | Minimize |
| CII rating penalty | $J_{CII}$ | USD | Minimize |
| CVaR (tail cost risk) | $J_{CVaR}$ | USD | Minimize |

Currently, all objectives are aggregated into a single weighted sum:
$$J = w_1 J_{cost} + w_2 J_{GHG} + w_3 J_{delay} + w_4 J_{CII} + w_5 J_{CVaR}$$

---

## 2. Weighted Sum vs. Pareto Multi-Objective

### 2.1 Weighted Sum (Current)

**Advantages:**
- Simple, fast, single solution per run
- Allows direct comparison with Phase 4 results
- Interpretable for decision-makers

**Disadvantages:**
- Weights must be specified a priori
- Cannot reveal trade-off structure
- Different weight choices may give very different "optimal" solutions
- Weight tuning is subjective and operationally unjustifiable

### 2.2 Pareto Multi-Objective Formulation

**Pareto dominance:** Solution $x$ dominates $x'$ if $J_k(x) \leq J_k(x')$ for all $k$ and $J_k(x) < J_k(x')$ for at least one $k$.

**Pareto front:** Set of non-dominated solutions. Decision-maker selects a point on the front based on operational preferences.

**Advantages:**
- Reveals trade-off structure
- No weight specification needed
- Richer decision support for operators

**Disadvantages:**
- More complex algorithm (archive management)
- Requires additional metric for comparison (hypervolume indicator)
- Phase 4 results are not directly comparable to Pareto front analysis

---

## 3. Multi-Objective QI Extensions

### 3.1 Multi-Objective QPSO (MO-QPSO)

**Mechanism:** Standard QPSO with:
- Pareto archive of non-dominated solutions (bounded size, e.g., 100)
- Guide particle selection from archive using crowding distance
- $gbest$ chosen randomly from archive (weighted by crowding distance)

**Literature:** Well-established (multiple papers 2010–2023). No major algorithmic novelty needed.

### 3.2 Multi-Objective QIEA (MO-QIEA)

**Mechanism:** QIEA with:
- External non-dominated archive
- Q-bit rotation guided by archive elite set (best in each objective dimension)
- Multi-directional rotation: Q-bits updated toward different archive members per objective

**Literature:** MOQIEA (Qian et al. 2013) — established framework.

### 3.3 Multi-Objective Hybrid QI-HFO

Combine MO-QIEA (for discrete/categorical) + MO-QPSO (for continuous speed):
- Pareto archive shared between both components
- Archive membership determined jointly by (cost, GHG, delay) objectives
- Crowding distance computed over all objectives

---

## 4. Recommended Strategy for Phase 5

**Phase 5 should NOT attempt full multi-objective optimization in the first iteration.**

Rationale:
1. Phase 4 established QPSO vs. DE comparison on single-objective
2. Phase 5 primary goal: demonstrate hybrid QI-HFO correctness and feasibility improvement
3. Multi-objective is a Phase 5.2 extension

**Phase 5 Strategy:**
1. Phase 5.0: Implement Hybrid QI-HFO with single-objective (matching Phase 4 budget)
2. Phase 5.1: Demonstrate 100% feasibility rate (fixing Phase 4.1 root cause)
3. Phase 5.2: Add multi-objective Pareto extension
4. Phase 5.3: Full sensitivity and uncertainty study

---

## 5. Hypervolume Indicator

For Pareto multi-objective comparison, use **Hypervolume Indicator (HV)**:
$$HV(A, r) = \lambda(\bigcup_{a \in A} [a, r])$$

where $A$ is the Pareto archive, $r$ is a reference point (typically 10% worse than nadir), and $\lambda$ is Lebesgue measure.

A higher HV indicates a better Pareto front (more spread, closer to ideal).

**Implementation:** `pygmo` or `deap` libraries provide hypervolume computation. Both are standard Python packages.
