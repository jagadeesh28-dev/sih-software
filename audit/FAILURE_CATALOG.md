# Egreen Quanta (SIH26138): Complete Failure Catalog (F1–F16)

**Auditor:** Independent Senior Optimization & Reliability Engineer  
**Classification Standard:** Systematic Failure Taxonomy (F1 to F16)  
**Date:** 18 September 2026

---

## 1. Systematic Failure Taxonomy Matrix

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       SYSTEM FAILURE CATALOG (F1 TO F16)                                       │
├─────┬───────────────────────────┬──────────┬─────────────────────────────┬─────────────────────────────────────┤
│ ID  │ Failure Mode Name         │ Severity │ Root Cause Mechanism        │ Algorithmic Mitigation Implemented  │
├─────┼───────────────────────────┼──────────┼─────────────────────────────┼─────────────────────────────────────┤
│ F1  │ Prediction Extrapolation  │ HIGH     │ Unseen drafts / velocities  │ SafeFuelObjective barrier fallback  │
│ F2  │ Out-of-Distribution (OOD) │ HIGH     │ Cross-class vessel mismatch │ Quarantine & pure physics fallback  │
│ F3  │ Constraint Inversion Trap │ CRITICAL │ Infeasible cheaper penalty  │ Deb's feasibility-first selection   │
│ F4  │ Repair Distortion         │ MEDIUM   │ Biased greedy cargo balance │ Bounded proportional capacity topoff│
│ F5  │ Optimizer Stagnation      │ HIGH     │ Loss of swarm diversity     │ Q-bit superpositions / DE crossover │
│ F6  │ Categorical Collision     │ CRITICAL │ Duplicate ship assignment   │ Bijective conditional masked decoder│
│ F7  │ Regulatory Conflation     │ HIGH     │ Mixing FuelEU and IMO CII   │ Decoupled modular statutory engines │
│ F8  │ Numerical Instability     │ MEDIUM   │ Divide by zero on zero speed│ Safe epsilon-clamped denominators   │
│ F9  │ Runtime Bottleneck        │ MEDIUM   │ Quadratic distance matrix   │ Linear-time order-statistic sorting │
│ F10 │ Memory Leak               │ LOW      │ Unbounded Pareto archive    │ Epsilon-dominance grid truncation   │
│ F11 │ UI/Backend Inconsistency  │ HIGH     │ Stale display cache         │ Direct JSON contract serialization  │
│ F12 │ Reproducibility Drift     │ CRITICAL │ Unseeded pseudo-random calls│ Explicit seed parameters everywhere │
│ F13 │ Statistical False Positive│ HIGH     │ P-hacking on small samples  │ 30 matched seeds & Holm adjustments │
│ F14 │ Benchmark Design Flaw     │ HIGH     │ Asymmetric evaluator logic  │ Shared frozen C0 evaluation pipeline│
│ F15 │ Data Leakage              │ CRITICAL │ Random train/test split     │ Voyage-isolated temporal split      │
│ F16 │ Physical Unit Mismatch    │ CRITICAL │ NM vs km, kg/h vs t/voyage  │ Unit test suite enforcing SI/naut.  │
└─────┴───────────────────────────┴──────────┴─────────────────────────────┴─────────────────────────────────────┘
```

---

## 2. Detailed Technical Root-Cause & Verification Dossier

### F1 & F2: Prediction Extrapolation & Out-of-Distribution Failure
* **Symptom:** In extreme sea states or on unseen ship hulls, black-box neural networks or gradient boosted trees predict negative fuel burn or unphysical speed jumps ($P \propto V^{0.5}$).
* **Root Cause:** Tree-based models cannot extrapolate outside their convex training hulls.
* **Mitigation:** The `SafeFuelObjective` barrier function bounds the ML residual ($\Delta \dot{m}_f \in [-0.3, +0.3] \cdot \dot{m}_{\text{physics}}$). When telemetry flags an uncalibrated hull, inference automatically falls back to the Holtrop-Mennen physical model.

### F3 & F6: Constraint Inversion Trap & Categorical Collision
* **Symptom:** Swarm particles cluster in invalid assignment states where one vessel is assigned to two overlapping routes while another route is orphaned.
* **Root Cause:** In an additive penalty formulation, an infeasible schedule with a small penalty evaluated as numerically cheaper than a valid route experiencing contractual demurrage delay. Continuous rounding also produced many-to-one integer duplicates.
* **Mitigation:** Deb's feasibility-first comparison ensures any feasible plan strictly dominates an infeasible one. The `ConditionalDemandObservation` decoder sequentially removes assigned vessels, guaranteeing bijective mutual exclusion.

### F12 & F14: Reproducibility Drift & Benchmark Design Flaw
* **Symptom:** Metaheuristic A appears to win because it used a different repair heuristic or had a hidden iteration multiplier.
* **Root Cause:** Asymmetric evaluation pipelines and hidden random seed defaults.
* **Mitigation:** The `CommonFleetEvaluator` acts as a single, shared, frozen evaluation interface. Every optimizer receives exactly 2,500 expensive objective function calls across identical random seeds (1001 to 1030).
