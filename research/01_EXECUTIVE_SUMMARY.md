# 01 — EXECUTIVE SUMMARY
## SIH26138 Quantum-Inspired Optimization: Literature Investigation & Algorithm Selection

**Date:** September 14, 2026  
**Role:** Senior Stochastic-Optimization Researcher / Adversarial Scientific Auditor  
**Scope:** RQ1–RQ22; 23-document research deliverable  
**Git Commit Baseline:** `20309b214b9540a7363b7365e442a222cd9c49a1`  

---

## Central Conclusion

**OPTION C: BUILD HYBRID QI FRAMEWORK**

A hybrid Quantum-Inspired framework combining:
- **QIEA-style probabilistic representations** for binary/categorical variables (shore power, fuel mode, demand assignment)
- **Adapted QPSO continuous-space search** for speed/cargo
- **Feasibility-first constraint handling** replacing penalty inversion

is justified, defensible, and constitutes a research contribution beyond prior art when applied to real-telemetry-calibrated heterogeneous maritime fleet optimization under IMO CII and FuelEU Maritime constraints.

This is NOT a claim that the algorithm will outperform DE. It is a claim that:
1. The representation is more appropriate for the heterogeneous mixed-variable structure.
2. The constraint-handling failure experienced by QPSO is an **implementation choice** (penalty-only), not an inherent QPSO limitation.
3. A hybrid architecture can be scientifically justified.
4. No prior art exists combining all five features simultaneously in a maritime fleet context.

---

## Key Findings Summary

### What Went Wrong with QPSO (Phase 4.1)
The forensic audit conclusively identified **Penalty Inversion** as the primary failure mechanism. QPSO's failure on 4/30 seeds is **not evidence that QPSO is fundamentally inferior to DE**. It is evidence that:
- The continuous QPSO framework applied to categorical demand assignments without a feasibility-first rule creates attractor trapping when penalty magnitudes are miscalibrated relative to soft penalty values.
- This is a **representation and constraint-handling defect**, not an irreducible algorithmic one.

### Literature on QPSO Limitations
Peer-reviewed literature (ResearchGate, arXiv, IEEE) **does support** the observation that standard QPSO struggles with categorical and mixed-integer variables. The mechanism is well-documented: the quantum-well position update operates in $\mathbb{R}^D$ and has no manifold awareness for combinatorial spaces. This is a **literature-supported limitation** (Evidence Class A).

### What Literature Says About Alternatives
1. **QIEA/QGA with Q-bit representation** is specifically designed for binary and combinatorial variables. It naturally handles shore-power (binary), fuel selection (categorical), and demand assignment (categorical).
2. **Hybrid QPSO-QIEA architectures** are described in literature but have NOT been applied to heterogeneous maritime fleet optimization under regulatory constraints and alternative fuel scenarios.
3. **Quantum-Inspired Differential Evolution (QIDE)** replaces DE's continuous-valued mutation with Q-bit probability sampling. For our problem, this provides marginal algorithmic benefit since DE already achieves 100% feasibility.
4. **No prior art** directly combines: (a) heterogeneous QI representation, (b) real telemetry-calibrated surrogate models, (c) multi-weather CVaR robustness, (d) IMO CII + FuelEU Maritime constraints, and (e) alternative fuel cost/GHG modeling in a joint framework.

### Commercial Prior Art (Does Not Block Academic Novelty)
Commercial systems (Wärtsilä FOS, Kongsberg K-Fleet, ABB OCTOPUS) solve continuous speed and route optimization and produce CII compliance reports. They do NOT:
- Use quantum-inspired metaheuristics
- Optimize fuel-type assignment jointly with speed
- Handle multi-fuel alternative technology scenarios with GHG pathway modeling
- Expose algorithmic internals for academic benchmarking

### Research Gap Assessment
The demonstrable gap is:
> **No published work applies a heterogeneous quantum-inspired representation (binary + categorical probability distributions + continuous quantum-potential search) to multi-vessel fleet scheduling with hard assignment constraints, alternative fuel scenarios, regulatory CII/FuelEU compliance, and real-data surrogate calibration under a scientifically fair equal-budget benchmark.**

---

## Final Recommendation Overview

| Question | Answer |
|:---|:---|
| Continue with QPSO? | Yes, as component; add QIEA for categorical |
| Add QIEA/QGA? | **Yes — for assignment/fuel/shore decisions** |
| Investigate QIDE? | Limited; marginal over DE in this context |
| Hybrid QI? | **Yes — Hybrid QIEA-QPSO is justified** |
| QPSO failure: algorithm or representation? | **Primarily representation + constraint handling** |
| Existing algorithm already solves it? | **No exact equivalent for maritime context** |
| Defensible research gap? | **Yes — narrow but demonstrable** |
| Can we design new algorithm? | **Yes — principled hybrid, not pure novelty** |
| SIH final architecture? | **Hybrid QI-HFO (Hybrid Quantum-Inspired Heterogeneous Fleet Optimizer)** |
