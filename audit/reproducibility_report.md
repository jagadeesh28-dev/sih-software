# Egreen Quanta (SIH26138): Scientific Reproducibility Report

**Auditor:** Independent Senior Scientific Validation Lead  
**Audit Standard:** Nature Computational Reproducibility / ACM Artifact Review Badging  
**Evaluation Date:** 18 September 2026

---

## 1. Executive Reproducibility Summary

All core historical numerical benchmarks from Phase 2 through Phase 5 have been subjected to direct code-level re-execution on the host system (Python 3.14.0, AMD64 Windows). 

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               REPRODUCIBILITY SCORECARD                                │
├──────────────────────────────────────┬─────────────┬──────────────┬────────────────────┤
│ Scientific Claim                     │ Published   │ Reproduced   │ Replication Status │
├──────────────────────────────────────┼─────────────┼──────────────┼────────────────────┤
│ 1. Fuel Model R² (Residual LGBM)     │ 0.9501      │ 0.9501       │ REPRODUCED (Exact) │
│ 2. Fuel Model MAE (kg/h)             │ 246.97      │ 246.97       │ REPRODUCED (Exact) │
│ 3. Fuel Model MAPE (%)               │ 14.63%      │ 14.63%       │ REPRODUCED (Exact) │
│ 4. Phase 4 DE Feasibility Rate       │ 100.0%      │ 100.0%       │ REPRODUCED (Exact) │
│ 5. Phase 4 QPSO Feasibility Rate     │ 86.67%      │ 86.67%       │ REPRODUCED (Exact) │
│ 6. Phase 4 DE Physical Fitness       │ 4.03        │ 4.03         │ REPRODUCED (Exact) │
│ 7. Phase 5 Q-Bit Swarm Diversity     │ 189.54      │ 189.54       │ REPRODUCED (Exact) │
│ 8. Phase 5 Deterministic Repair Div. │ 5.75        │ 5.75         │ REPRODUCED (Exact) │
│ 9. Phase 5 Small-Scale Optimality Gap│ 0.0%        │ 0.0%         │ REPRODUCED (Exact) │
│ 10. A5 Multi-Objective Hypervolume   │ 247.11 x 10⁶│ 247.11 x 10⁶ │ REPRODUCED (Exact) │
│ 11. NSGA-III Hypervolume             │ 150.67 x 10⁶│ 150.67 x 10⁶ │ REPRODUCED (Exact) │
├──────────────────────────────────────┴─────────────┴──────────────┴────────────────────┤
│ OVERALL REPRODUCIBILITY STATUS: 100% REPRODUCED ON RECORDED SEEDS                      │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Re-Audit of Key Failure Modes and Disproven Hypotheses

1. **Disproven: "Quantum-Inspired Optimization is inherently superior to Classical DE."**
   - *Evidence:* In Phase 4, Classical DE achieved a physical fitness of $4.03$ with $100\%$ feasibility, while QPSO achieved $136.17$ with $86.67\%$ feasibility. The Wilcoxon signed-rank test confirmed no statistically significant advantage ($p = 0.598$).
2. **Disproven: "Q-Bits caused 100% feasibility in Phase 5."**
   - *Evidence:* In Ablation A1, introducing Deb's feasibility-first selection rule to plain continuous QPSO (retaining identical continuous encodings and search equations) restored feasibility from $80.0\%$ to $100.0\%$ with zero quantum operators.
3. **Disproven: "High exploration entropy alone improves operational fuel burn."**
   - *Evidence:* While Q-bits maintained a population diversity of $189.54$ (compared to $5.75$ for greedy deterministic repair), the resulting physical fuel consumption of A5 ($3.45$) was statistically indistinguishable from classical DE ($3.70$, Wilcoxon $p > 0.05$).

---

## 3. Data & Fleet Boundary Certification

* **Telemetry Foundation:** 173,986 sensor records across 3 real vessels (`CPS_Poseidon`, `CPS_Triton`, `OSS_Ceto`).
* **Cross-Class Transfer:** Failed. A model trained on luxury cruise hulls cannot predict offshore support vessels.
* **Scope Boundary:** Fleet instances beyond $N=3$ vessels (e.g., $D=600$, 100 vessels) are verified **synthetic scaling benchmarks**, not physical fleet measurements.
