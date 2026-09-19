# Phase 5: Heterogeneous Quantum-Inspired Fleet Optimization & A0–A5 Scientific Ablation
## Project: Egreen Quanta (SIH26138)
**"Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization"**

---

## 1. Executive Overview

Phase 5 addresses the central scientific inquiry of the SIH26138 research platform:
> **"Which component actually fixes the Phase 4 QPSO combinatorial assignment failure, and does the resulting hybrid QI framework provide a statistically and practically meaningful advantage over classical optimization methods?"**

Rather than manufacturing artificial superiority or presenting inflated claims of quantum computing advantage, Phase 5 executes a mathematically rigorous, fully reproducible **A0–A5 ablation study** across 30 matched random seeds (1001–1030) under a frozen evaluation budget of 2,500 calls per run.

### Key Empirical Findings
1. **Root Cause Confirmed**: 100% of Phase 4 QPSO failures were caused by combinatorial demand collisions trapped by penalty inversion (hard assignment penalty of $\$51,000$ beat temporary rough-weather schedule delays of up to $\$109,292$).
2. **Deb's Feasibility-First Selection (A1)**: Completely cures the feasibility failure, increasing run feasibility from **80.0% to 100.0%** without altering representation or continuous QPSO equations.
3. **Deterministic Repair (A2)**: Guarantees 100% feasibility and achieves lowest scalar fitness (3.39), but collapses swarm diversity (5.75 vs. 176.23).
4. **Standalone Q-Bit Representation (A4)**: Restores 100% feasibility while preserving high swarm diversity (189.54).
5. **Full Hybrid Framework (A5)**: Achieves 100% feasibility, zero penalty, and dominates classical baselines in **Pareto Hypervolume** ($247.11 \times 10^6$ vs. $150.67 \times 10^6$ for NSGA-III).
6. **Friedman Omnibus Significance**: $\chi^2 = 91.03$, $p = 1.85 \times 10^{-17}$, confirming statistically significant differences across the panel.
7. **DE vs. Hybrid QI Verdict**: DE remains an exceptionally strong classical single-objective solver. A5 achieves comparable scalar operational fitness while providing superior multi-objective trade-off coverage, hypervolume, and CVaR uncertainty robustness.

---

## 2. Directory Structure and Manifest

```
PHASE5/
├── README.md                         # This executive guide
├── PHASE5_ARCHITECTURE.md            # Technical architecture of Option C Hybrid QI-HFO
├── PHASE5_MATHEMATICAL_MODEL.md      # Multi-objective, CVaR risk, and constraint formulations
├── PHASE5_ALGORITHM_SPECIFICATION.md # Formal pseudocode and update equations (QIEA, QPSO, Deb)
├── PHASE5_ABLATION_PROTOCOL.md       # A0–A5 hypothesis testing and component contribution
├── PHASE5_BENCHMARK_PROTOCOL.md      # 30-seed matched benchmarking protocol & budget accounting
├── PHASE5_STATISTICAL_PROTOCOL.md    # Non-parametric hypothesis tests, Holm correction, BCa CIs
├── PHASE5_FAILURE_ANALYSIS.md        # 10-class failure taxonomy & forensic trajectory traces
├── PHASE5_REPRODUCIBILITY.md         # Environment manifest, package versions, and audit hashes
├── PHASE5_NOVELTY_AUDIT.md           # Prior art analysis vs. Han 2023, patents, and commercial tools
├── PHASE5_CLAIM_LEDGER.yaml          # Formal audit ledger for Claims 1–8
├── PHASE5_FINAL_REPORT.md            # 28-section comprehensive final scientific report
├── PHASE5_SIH_STORY.md               # Scientific narrative for SIH 2026 evaluation jury
│
├── results/                          # Standardized CSV benchmark logs
│   ├── A0.csv                        # Plain QPSO runs (N=30)
│   ├── A1.csv                        # QPSO + Deb's rules runs (N=30)
│   ├── A2.csv                        # QPSO + Decoder/Repair runs (N=30)
│   ├── A3.csv                        # Discrete QPSO runs (N=30)
│   ├── A4.csv                        # Heterogeneous Q-bit + QPSO runs (N=30)
│   ├── A5.csv                        # Complete Hybrid QI runs (N=30)
│   ├── DE.csv                        # Differential Evolution runs (N=30)
│   ├── PSO.csv                       # Canonical PSO runs (N=30)
│   ├── GA.csv                        # Genetic Algorithm runs (N=30)
│   ├── Random.csv                    # Unguided Uniform Random Search runs (N=30)
│   ├── NSGA3.csv                     # NSGA-III runs (N=30)
│   ├── A5_ABLATION_TABLE.csv         # Master performance ablation matrix
│   ├── A5_COMPONENT_CONTRIBUTION.csv # Pairwise component contribution statistics
│   └── statistics.csv                # Complete omnibus and pairwise statistical tests
│
├── figures/                          # 18 publication-quality figures
│   ├── 01_A0_vs_A1_feasibility.png
│   ├── 02_A0_vs_A2_repair.png
│   ├── 03_A2_vs_A3_discrete_search.png
│   ├── 04_A3_vs_A4_qbit_contribution.png
│   ├── 05_A4_vs_A5_multiobjective.png
│   ├── 06_all_algorithm_convergence.png
│   ├── 07_feasibility_rate.png
│   ├── 08_candidate_feasibility.png
│   ├── 09_constraint_failure_taxonomy.png
│   ├── 10_pareto_front.png
│   ├── 11_hypervolume_comparison.png
│   ├── 12_scalability.png
│   ├── 13_runtime_scalability.png
│   ├── 14_qpso_failure_seed_1005.png
│   ├── 15_qpso_failure_seed_1021.png
│   ├── 16_qpso_failure_seed_1025.png
│   ├── 17_qpso_failure_seed_1029.png
│   └── 18_small_scale_optimality_gap.png
│
└── validation/
    ├── small_exact.csv               # Level 1 exact exhaustive validation (J* = 873.23)
    ├── failure_taxonomy.csv          # 10-class failure frequency matrix
    └── scalability.csv               # D=30 to D=600 scalability benchmark
```

---

## 3. One-Command Reproduction

To reproduce all benchmarks, statistical tests, validation tables, and publication figures:
```bash
python run_phase5.py
```
To run unit verification tests:
```bash
python -m pytest tests/test_phase5_verification.py -v
```
