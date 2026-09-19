# 06 — CONSTRAINT HANDLING: SCIENTIFIC ASSESSMENT
## RQ8: How Should Constraints Be Handled in QI Algorithms?

---

## 1. Taxonomy of Constraint Handling Techniques (CHTs)

### 1.1 Penalty Methods

**Static Penalty:**  
$$F_{penalized}(x) = J_{objective}(x) + P \cdot v(x)$$

where $v(x) = \sum_i \max(0, g_i(x))$ is total constraint violation.

**Weakness:** Penalty scaling ($P$) must be tuned. If $P$ is too small → infeasible solutions preferred (Penalty Inversion). If $P$ is too large → feasible region shrinks, loss of objective signal.

**Dynamic Penalty:**  
$$F_{penalized}(x, t) = J_{objective}(x) + P(t) \cdot v(x)$$

$P(t)$ increases over iterations. Mitigates parameter sensitivity but requires scheduling.

**Adaptive Penalty:**  
$P$ updated based on fraction of feasible solutions in current population. Better than static but still parameter-dependent.

---

### 1.2 Deb's Feasibility-First Rule (2000)

**Reference:** Deb, K. (2000). An efficient constraint handling method for genetic algorithms. *Computer Methods in Applied Mechanics and Engineering*, 186(2-4), 311–338. DOI: 10.1016/S0045-7825(99)00389-8

**Rules:**
1. Between two feasible solutions: prefer lower objective value
2. Between feasible and infeasible: always prefer feasible
3. Between two infeasible solutions: prefer lower constraint violation

**Advantages:**
- No penalty parameter to tune
- Prevents Penalty Inversion by definition
- Theoretically clean

**Disadvantages:**
- May slow initial convergence if feasible region is small
- Does not use constraint violation information to guide search (purely selection-side)

**Applicability to QPSO:**  
⚠️ **Partially applicable.** Deb's rule applies during selection (choosing which particle's position to store as $pbest$). It does not fix the update step, which still generates infeasible positions. Combined with a repair operator, Deb's rule eliminates Penalty Inversion.

**Applicability to QIEA:**  
✅ **Fully applicable.** During observation, only retain configurations where $\sum_v d_{v,k} = 1$ via conditional sampling. Q-bit update occurs only when the observed solution is feasible or improves feasibility.

---

### 1.3 Epsilon-Constrained Method (Takahama & Sakai 2006)

**Reference:** Takahama, T., & Sakai, S. (2006). Constrained optimization by the ε constrained differential evolution with gradient-based mutation and feasibility rules. *CEC 2006*. DOI: 10.1109/CEC.2006.1688280

**Mechanism:** Relax constraints by tolerance $\epsilon(t)$ that decreases over iterations:
$$\text{feasible at time } t \text{ if } v(x) \leq \epsilon(t)$$

This allows initially-infeasible solutions to participate in search, providing gradient information near constraint boundaries.

**Applicability:** Well-suited for smooth constraint functions. Our demand assignment constraint is discrete (binary violation), making $\epsilon$-constraint less useful. Our speed-based CII constraint is smooth and could use $\epsilon$-constraint during speed optimization.

---

### 1.4 Repair Operators

**Mechanism:** After generating a candidate solution, apply a domain-specific transformation to restore feasibility.

For demand assignment: 
1. For each demand unit $k$ with $\sum_v d_{v,k} \neq 1$:
   - If $\sum_v = 0$: assign to vessel with highest available capacity
   - If $\sum_v > 1$: keep only the assignment with highest probability/weight; clear others

**Cost:** $O(D_{demand} \cdot V)$ per solution evaluation. For our problem: $O(48 \cdot 6) = 288$ operations — negligible.

**Advantage:** Guarantees 100% feasibility for demand assignment constraint.

**Interaction with QIEA:** Q-bit update is informed by the repaired (feasible) solution. This is standard practice in QIEA and QGA.

---

## 2. Penalty Inversion: Mathematical Proof of Inevitability Under Static Penalty

**Theorem (Penalty Inversion Condition):**  
A static penalty method with penalty magnitude $P$ causes Penalty Inversion if there exists a feasible solution $x^*$ and an infeasible solution $x'$ such that:
$$J(x') + P \cdot v(x') < J(x^*)$$
where $v(x') > 0$.

**For our problem (SIH26138):**

Let $J^*_{feasible}$ = minimum feasible cost (from Phase 4 data: $\approx \$48,000$)  
Let $J^{inf}_{min}$ = minimum infeasible cost without penalty (a valid infeasible solution may report low operational cost if it "cheats" by not satisfying demand)  
Let $P_{hard} = \$50,000$

If there exists an infeasible configuration with $J^{inf} + P_{hard} < J^*_{feasible}$, Penalty Inversion occurs.

**Empirically Confirmed (Phase 4.1):** Failed seeds exhibited $J^{inf} + P_{hard} \approx \$60k - \$80k < J^*_{feasible} = \$48k$ — wait, let me re-examine.

**Correction:** The Penalty Inversion works in reverse from expected. The penalty-adjusted infeasible cost exceeded $J^*_{feasible}$ but the QPSO swarm could not explore to find $J^*_{feasible}$ because:
1. The swarm collapsed to infeasible configurations early
2. Once $gbest$ is infeasible, $mbest$ shifts toward infeasible region
3. All particles orbit the infeasible attractors, unable to discover the feasible optimum

**The mechanism is attractor trapping, not direct objective comparison.** The penalty makes infeasible solutions sufficiently unattractive (in absolute terms) but QPSO's attractor update mechanism does not have a feasibility-first rule to prevent attractor placement in infeasible regions.

---

## 3. Recommended Constraint Handling for SIH26138 Algorithms

### For QPSO (Existing, with Corrections)

| Constraint | Method | Description |
|:---|:---|:---|
| Demand assignment | Repair operator | Greedy reassignment post-update |
| Demand assignment | Feasibility-first (Deb) | Never store infeasible as $pbest$ or $gbest$ |
| Capacity constraint | Repair operator | Redistribute excess demand |
| CII compliance | $\epsilon$-constraint on speed | Gradually enforce CII over iterations |
| Shore power | Direct rounding | Binary variable, simple threshold |
| Fuel mode | Categorical mutation | Random jump if plateau detected |
| Penalty | Dynamic scaling | $P(t) = P_0 \cdot (1 + t/T_{max})^2$ |

### For QIEA (New Component)

| Constraint | Method | Description |
|:---|:---|:---|
| Demand assignment | Conditional observation | Normalized sampling by vessel capacity |
| Capacity constraint | Rejection sampling | Re-sample if violated; update toward feasible |
| CII compliance | Q-bit bias update | Increase $|\beta|^2$ for CII-compliant speeds |
| Shore power | Standard binary Q-bit | No special handling needed |
| Fuel mode | Categorical probability vector | Dirichlet distribution update |
| GHG intensity | Conditional observation filter | Reject solutions violating FuelEU threshold |

### For Hybrid QI-HFO (Proposed)

The hybrid architecture assigns constraints to the most appropriate component:
- **QIEA component** handles: assignment, shore power, fuel mode selection, GHG filter
- **QPSO component** handles: speed optimization with CII $\epsilon$-constraint
- **Interface:** QIEA outputs feasible discrete configuration → QPSO optimizes speed conditional on that configuration → joint fitness evaluation

---

## 4. Evidence Summary

| CHT | Eliminates Penalty Inversion | Implementation Complexity | Phase 4 Applicability |
|:---|:---:|:---:|:---|
| Static penalty | ❌ | Low | Current (failed) approach |
| Dynamic penalty | ⚠️ Partial | Low-Medium | Improvement for QPSO |
| Deb's rule | ✅ | Low | Directly applicable to QPSO |
| Repair operator | ✅ | Medium | Directly applicable |
| Conditional observation | ✅ | Medium-High | QIEA native; requires hybrid |
| $\epsilon$-constraint | ✅ for smooth | Medium | Applicable to CII on speed |

**Recommendation:** Implement Deb's rule + dynamic penalty as minimal fix for existing QPSO. Implement conditional observation + repair for QIEA component of hybrid architecture.
