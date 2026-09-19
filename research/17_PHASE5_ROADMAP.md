# 17 — IMPLEMENTATION ROADMAP FOR PHASE 5
## RQ22: What Should Phase 5 Build and Test?

---

## 1. Phase 5 Objectives

Derived from Phase 4.1 forensic audit and this literature investigation:

1. **Fix QPSO** — Apply Deb's rule + dynamic penalty + repair operator → achieve 100% feasibility
2. **Implement Hybrid QI-HFO** — QIEA component for categorical/binary + QPSO for speed
3. **Benchmark comparatively** — QPSO-fixed vs. DE vs. Hybrid vs. QPSO-original (30 seeds each)
4. **Validate multi-objective extension** — Optional Pareto mode

---

## 2. Implementation Order (Dependency Graph)

```
Phase 5.0: QPSO Patch
├── 5.0.1: Implement Deb's feasibility rule in QPSO pbest/gbest update
├── 5.0.2: Implement dynamic penalty scaling
├── 5.0.3: Implement demand assignment repair operator
└── 5.0.4: Benchmark QPSO-patched vs. QPSO-original (30 seeds)
    → Expected: feasibility rate increases to 100%
    → If not 100%, diagnose residual failures before proceeding

Phase 5.1: QIEA Component
├── 5.1.1: Implement Q-bit matrix representation
├── 5.1.2: Implement conditional observation for demand assignment
├── 5.1.3: Implement Dirichlet-Q categorical vector for fuel mode
├── 5.1.4: Implement quantum rotation gate update
├── 5.1.5: Unit tests for each component (100% pass required)
└── 5.1.6: Standalone QIEA benchmark on discrete-only subproblem

Phase 5.2: Hybrid QI-HFO Integration
├── 5.2.1: Interface QIEA → fitness evaluator (discrete variables only)
├── 5.2.2: Interface QPSO → fitness evaluator (speed only)
├── 5.2.3: Joint fitness evaluation: QIEA discrete + QPSO speed → J
├── 5.2.4: Shared Deb's rule selection across both components
├── 5.2.5: Integration tests (full optimization loop)
└── 5.2.6: Full benchmark: Hybrid vs. DE vs. QPSO-patched (30 seeds each)

Phase 5.3: Validation
├── 5.3.1: Sensitivity analysis (parameter perturbation ±20%)
├── 5.3.2: Scaling study (4, 6, 8 vessels)
├── 5.3.3: Alternative fuel scenario testing
└── 5.3.4: Weather CVaR robustness study (50 scenarios)
```

---

## 3. File Structure for Phase 5 Implementation

```
sih26138_platform/
├── optimization/
│   ├── qpso.py                    # EXISTING — to be patched
│   ├── differential_evolution.py  # EXISTING — keep unchanged
│   ├── qiea.py                    # NEW — QIEA component
│   ├── hybrid_qihfo.py            # NEW — hybrid integrator
│   └── constraint_handlers.py     # NEW — Deb's rule, repair operators
├── tests/
│   ├── test_qiea.py               # NEW — unit tests for QIEA
│   ├── test_hybrid.py             # NEW — integration tests
│   └── test_constraint_handlers.py # NEW — CHT tests
├── experiments/
│   └── optimization_phase5/       # NEW — results
└── research/
    └── (this document set)        # EXISTING
```

---

## 4. Unit Test Requirements for Phase 5

All new components must achieve 100% test coverage on:

### QIEA Tests
```python
# test_qiea.py (minimum test set)

def test_qbit_initialization():
    """Q-bits initialize to uniform distribution (|α|²=|β|²=0.5)."""

def test_binary_observation():
    """Binary observation produces 0 or 1 values only."""

def test_categorical_observation():
    """Categorical observation produces valid fuel mode indices only."""

def test_conditional_demand_observation_partition():
    """Demand assignment satisfies sum_v d[v,k]=1 for all k."""

def test_conditional_demand_observation_capacity():
    """Demand assignment respects vessel capacity constraints."""

def test_rotation_gate_direction():
    """Rotation gate increases probability toward best solution bit."""

def test_dirichlet_update_normalization():
    """Dirichlet-Q update maintains sum(p_k)=1."""

def test_dirichlet_floor():
    """Dirichlet-Q update maintains minimum probability floor."""

def test_qiea_convergence_trivial():
    """QIEA converges on trivial 1-variable binary problem (optimal = 1)."""

def test_catastrophic_mutation():
    """Catastrophic mutation generates valid Q-bit configuration."""
```

### Constraint Handler Tests
```python
# test_constraint_handlers.py

def test_deb_prefers_feasible_over_infeasible():
    """Deb's rule always prefers feasible over infeasible."""

def test_deb_prefers_lower_cost_when_both_feasible():
    """Deb's rule selects lower objective when both feasible."""

def test_repair_operator_demand_partition():
    """Repair always produces valid demand assignment."""

def test_dynamic_penalty_increases_over_time():
    """Dynamic penalty increases monotonically."""

def test_no_penalty_inversion_after_repair():
    """After Deb's rule + repair, penalty inversion is impossible."""
```

---

## 5. Key Success Metrics for Phase 5

| Metric | Target | Statistical Test |
|:---|:---:|:---|
| QPSO-patched feasibility rate | 100% | Binomial exact |
| Hybrid QI-HFO feasibility rate | 100% | Binomial exact |
| Hybrid objective vs. DE | Non-inferior (CI includes 0) | Wilcoxon + BCa CI |
| Phase 5 total runtime (30 seeds × 4 algorithms) | < 4 hours | Wall clock |
| Test coverage | 100% (new files) | pytest-cov |
| All 120 Phase 4 tests | Still passing | pytest |

---

## 6. Decision Tree for Phase 5 Continuation

```
After Phase 5.0 (QPSO patched):
├── Feasibility rate = 100%? 
│   ├── YES → Continue to Phase 5.1
│   └── NO → Return to forensic audit (additional failure modes)
│
After Phase 5.2 (Hybrid benchmarked):
├── Hybrid feasibility = 100%?
│   ├── NO → Debug QIEA conditional observation implementation
│   └── YES → Continue
├── Hybrid objective ≥ DE (non-inferior)?
│   ├── YES → Proceed to Phase 5.3 (full validation)
│   └── NO → Report as honest negative result; analyze why
│
After Phase 5.3:
└── Compile full research report for SIH 2026 / journal submission
```

---

## 7. Risk Register for Phase 5

| Risk | Likelihood | Severity | Mitigation |
|:---|:---:|:---:|:---|
| QPSO patch increases runtime significantly | Low | Low | Profile; repair operator is O(V·D) |
| Hybrid is harder to implement than designed | Medium | Medium | Modular implementation; unit tests first |
| Hybrid does NOT outperform DE | Medium | Low | Acceptable; report as negative result |
| QIEA requires extensive parameter tuning | Medium | Medium | Use Han & Kim (2002) default parameters |
| 30 seeds insufficient to detect small effect | Medium | Low | Acceptable; power analysis in paper |
