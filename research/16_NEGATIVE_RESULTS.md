# 16 — NEGATIVE RESULTS PRESERVATION
## RQ21: What Negative Results Must Be Preserved and Reported?

---

## 1. The Scientific Value of Negative Results

The MASTER PROMPT for this investigation was explicit:
> "A negative result is acceptable and must be preserved if it is scientifically correct."
> "Do NOT optimize for impressive-looking results."

This section catalogs all negative results that must be preserved in any publication or presentation of SIH26138 work.

---

## 2. Catalog of Negative Results

### NR-1: QPSO Does Not Achieve 100% Feasibility

**Result:** QPSO achieves 86.67% feasibility (26/30 seeds feasible) on the Phase 4 benchmark.  
**Statistical support:** Binomial test; 95% Clopper-Pearson CI: [70.3%, 96.7%]  
**Honest interpretation:** QPSO has a structural limitation on this problem instance. The limitation is partly algorithmic (representation mismatch) and partly implementation (penalty inversion).  
**MUST NOT say:** "QPSO achieves comparable results to DE." (It does not, in feasibility.)  
**MUST say:** "QPSO and DE achieve statistically equivalent objective quality among feasible solutions, but QPSO exhibits a 13.33% infeasibility rate attributable to penalty inversion and categorical representation deficiencies."

---

### NR-2: QPSO and DE Are Statistically Indistinguishable in Objective Quality

**Result:** Wilcoxon p = 0.23 (after FWER correction). Hodges-Lehmann Δ = -$241, 95% BCa CI: [-$1,847, +$1,124].  
**Honest interpretation:** DE does NOT outperform QPSO in cost minimization on feasible solutions. Both algorithms find similar quality solutions when QPSO converges to feasibility.  
**This is a negative result for the hypothesis "QI algorithms find better solutions than classical DE."**  
**MUST preserve and report.** Cannot suppress this finding to make QPSO look better.

---

### NR-3: Phase 4 Benchmark Is Limited to a Single Problem Instance

**Result:** All 60 runs (30 QPSO + 30 DE) used the same 6-vessel fleet configuration with the same demand/port parameters, varying only random seed.  
**Honest interpretation:** Conclusions are valid for this problem instance but generalizability to other fleet sizes, route configurations, or demand distributions is not established.  
**MUST NOT say:** "The algorithm is validated for real-world maritime operations."  
**MUST say:** "Results are valid for the specific SIH26138 6-vessel benchmark configuration. Generalization requires additional experiments on varied problem instances."

---

### NR-4: Surrogate Models Are Not Fully Validated on Independent Data

**Result:** Telemetry surrogates were calibrated on training data and validated on a held-out test set. No prospective validation (predicting future fuel consumption on unseen voyages) was performed.  
**Honest interpretation:** Surrogate accuracy in deployment may differ from benchmark accuracy.  
**MUST preserve.** Any real-world deployment claim requires further validation.

---

### NR-5: The Research Gap Is Narrow

**Result:** While no prior work exactly combines all SIH26138 features, individual components (QIEA, QGA-maritime, QI-VRP) are well-studied.  
**Honest interpretation:** The novelty is in the specific combination, not in any fundamentally new algorithmic primitive.  
**MUST NOT say:** "We present an entirely new quantum-inspired algorithm."  
**MUST say:** "We present a principled hybrid of established quantum-inspired components (QIEA + QPSO) applied to a novel domain (heterogeneous maritime fleet with regulatory constraints and alternative fuels)."

---

### NR-6: Hybrid QI-HFO Has Not Yet Been Implemented or Benchmarked

**Result (as of Phase 4.1):** The Hybrid QI-HFO architecture described in Document 10 is a design proposal, not an implemented and validated algorithm.  
**Honest interpretation:** Claims about its performance are speculative. Phase 5 must implement and empirically validate before any performance claims are made.  
**MUST NOT say:** "Our hybrid algorithm outperforms DE." (No evidence exists for this claim.)  
**MUST say:** "We propose a hybrid architecture motivated by Phase 4.1 forensic analysis. Empirical validation is deferred to Phase 5."

---

### NR-7: QI Does Not Provide Quantum Speedup

**Result:** All algorithms (QPSO, DE, proposed hybrid) run on classical hardware. Computational complexity is $O(P \cdot D \cdot T)$ — no exponential speedup vs. classical alternatives.  
**Honest interpretation:** The "quantum-inspired" label refers to algorithmic design principles, not computational complexity advantages.  
**MUST preserve in any SIH or publication context.**

---

### NR-8: DE Achieves 100% Feasibility Without Special Constraint Handling

**Result:** Standard DE with penalty-only constraint handling achieves 100% feasibility on all 30 seeds.  
**Honest interpretation:** DE's mutation mechanism inherently provides diversity that avoids attractor trapping. QPSO's failure is not because penalty-only CHT is universally deficient — it is deficient for QPSO specifically.  
**MUST NOT misrepresent as "penalty-only CHT is always inadequate."**

---

## 3. Negative Result Preservation Protocol

All negative results must:
1. Appear in the main results section, not buried in supplementary material
2. Be stated in plain language alongside positive results
3. Include the statistical evidence
4. Include an honest interpretation
5. Not be contradicted by summary statements or abstract language

---

## 4. Context for SIH 2026

SIH judges evaluate scientific rigor, not just positive results. A platform that:
- Reports failures honestly (QPSO 86.67% feasibility)
- Diagnoses root causes (Penalty Inversion, categorical representation)
- Proposes evidence-based solutions (hybrid QI-HFO)
- Quantifies uncertainty (CVaR, bootstrap CI)

...is significantly stronger than one that cherry-picks positive results.

**Negative results, properly documented, demonstrate scientific integrity and strengthen the overall contribution.**
