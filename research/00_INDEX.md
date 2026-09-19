# SIH26138 RESEARCH CORPUS — INDEX
## Phase 4.1 Post-Audit Scientific Investigation
**Completed:** September 14, 2026 | **Status:** READY FOR PHASE 5

---

## Document Map

| # | Document | Focus | Key Deliverable |
|:---:|:---|:---|:---|
| 01 | [EXECUTIVE_SUMMARY](01_EXECUTIVE_SUMMARY.md) | Overview | Final verdict: Hybrid QI-HFO (Option C) |
| 02 | [QI_ALGORITHM_TAXONOMY](02_QI_ALGORITHM_TAXONOMY.md) | RQ1 | Full taxonomy of QI algorithms; comparison table |
| 03 | [QPSO_FORENSIC_ANALYSIS](03_QPSO_FORENSIC_ANALYSIS.md) | RQ2 | Mathematical root-cause; 4 failure modes |
| 04 | [QIEA_SUITABILITY](04_QIEA_SUITABILITY.md) | RQ3 | QIEA encoding for fleet problem; convergence proof |
| 05 | [MARITIME_QI_LITERATURE_SURVEY](05_MARITIME_QI_LITERATURE_SURVEY.md) | RQ4–7 | Prior art matrix; gap identification |
| 06 | [CONSTRAINT_HANDLING_ANALYSIS](06_CONSTRAINT_HANDLING_ANALYSIS.md) | RQ8 | CHT taxonomy; Deb's rule; conditional observation |
| 07 | [ALTERNATIVE_FUEL_MODELING](07_ALTERNATIVE_FUEL_MODELING.md) | RQ9 | LNG/Methanol/Bio-HFO; FuelEU Maritime formulation |
| 08 | [BENCHMARK_DESIGN](08_BENCHMARK_DESIGN.md) | RQ10 | Scientifically defensible benchmark protocol |
| 09 | [RESEARCH_GAP_ANALYSIS](09_RESEARCH_GAP_ANALYSIS.md) | RQ11–13 | Gap verification; 4 novelty tests |
| 10 | [HYBRID_QIHFO_ARCHITECTURE](10_HYBRID_QIHFO_ARCHITECTURE.md) | Design | Full pseudocode; update equations; parameters |
| 11 | [COMMERCIAL_PATENT_PRIORART](11_COMMERCIAL_PATENT_PRIORART.md) | RQ14–16 | Patent search; commercial system survey |
| 12 | [UNCERTAINTY_QUANTIFICATION](12_UNCERTAINTY_QUANTIFICATION.md) | RQ17 | CVaR formulation; surrogate uncertainty |
| 13 | [MULTIOBJECTIVE_EXTENSIONS](13_MULTIOBJECTIVE_EXTENSIONS.md) | RQ18 | Pareto/hypervolume; Phase 5 strategy |
| 14 | [STATISTICAL_METHODS](14_STATISTICAL_METHODS.md) | RQ19 | Wilcoxon; Holm-Bonferroni; BCa CI; power |
| 15 | [QUANTUM_CLAIMS_CLASSIFICATION](15_QUANTUM_CLAIMS_CLASSIFICATION.md) | RQ20 | QI vs. QC distinction; acceptable language |
| 16 | [NEGATIVE_RESULTS](16_NEGATIVE_RESULTS.md) | RQ21 | 8 negative results cataloged; preservation protocol |
| 17 | [PHASE5_ROADMAP](17_PHASE5_ROADMAP.md) | RQ22 | Implementation order; tests; risk register |
| 18 | [MATHEMATICAL_FORMALIZATION](18_MATHEMATICAL_FORMALIZATION.md) | Formal | Problem formulation; hybrid update equations |
| 19 | [SIH2026_POSITIONING](19_SIH2026_POSITIONING.md) | SIH | Innovation score; Q&A for judges |
| 20 | [EVIDENCE_LEDGER](20_EVIDENCE_LEDGER.md) | Audit | 23 claims × evidence class × strength |
| 21 | [REFERENCE_BIBLIOGRAPHY](21_REFERENCE_BIBLIOGRAPHY.md) | Refs | 27 APA 7th edition citations; Han 2023 highlighted |
| 22 | [OPEN_QUESTIONS](22_OPEN_QUESTIONS.md) | Future | 9 open questions; priority order |
| 23 | [FINAL_RECOMMENDATION](23_FINAL_RECOMMENDATION.md) | Verdict | Decision matrix; minimum defensible statement |

---

## Core Verdict (Three Sentences)

1. **QPSO's 13.33% infeasibility is an implementation defect** (Penalty Inversion + categorical representation mismatch), not an irreducible algorithmic limitation. It can be fixed without redesigning the algorithm.

2. **A Hybrid QI-HFO** combining QIEA's native binary/categorical Q-bit representation with QPSO's continuous-space quantum-well search, augmented by Deb's feasibility-first rule, is the scientifically justified architecture. It addresses a genuine, narrow research gap with no direct prior art in maritime fleet optimization.

3. **DE remains a strong competitive baseline** and may equal or outperform the hybrid — this is an empirical question for Phase 5, and a negative result is acceptable and publishable.

---

## Key Facts (Quick Reference)

| Fact | Value |
|:---|:---|
| QPSO feasibility rate (Phase 4) | 86.67% (26/30 seeds) |
| DE feasibility rate (Phase 4) | 100% (30/30 seeds) |
| QPSO vs. DE objective (feasible) | Wilcoxon p=0.23 (NS); Δ=−$241 |
| Phase 4.1 primary failure cause | Penalty Inversion ($50k hard < $109k soft) |
| Closest prior art | Han et al. 2023 (QGA, single vessel, CII) |
| Novel combination (confirmed absent) | QIEA+QPSO+Maritime+CII+FuelEU+AltFuels |
| Recommended algorithm | Hybrid QI-HFO (QIEA + QPSO + Deb's rule) |
| Phase 5 primary test | QPSO-patched + Hybrid vs. DE, 30 seeds |

---

## Total Research Corpus Size

- 23 documents
- ~152,000 characters
- 27 verified references (21 peer-reviewed, 6 industry/regulatory)
- 23 evidence claims classified by strength and class
