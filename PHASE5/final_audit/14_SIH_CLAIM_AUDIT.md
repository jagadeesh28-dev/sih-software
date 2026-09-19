# AUDIT #14: SIH JURY CLAIMS & COMPETITION AUDIT
**Project:** SIH26138 — Egreen Quanta  
**Audit Section:** §17 SIH Claim Audit & Jury Review  
**Auditors:** SIH 2026 Technical Architect & Scientific Validation Engineer  
**Date:** September 15, 2026  

---

## 1. Audit of Competition Claims (C1 to C15)

Every major claim proposed for presentation to the SIH 2026 Grand Finale jury was audited against empirical logs, statistical tests, and reproducibility standards:

| Claim ID | Formal Claim Statement | Empirical Evidence | Statistical Support | Causal Strength | Audit Verdict | Final Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **C1** | Plain QPSO (A0) reproduces Phase 4 assignment failure | `A0.csv`: 6 failed runs out of 30 (80.0% feasibility) | Exact seed match (1021, 1025, 1029) | Decisive | Replicated Phase 4 failure mode | **VERIFIED** |
| **C2** | Deb's feasibility-first rule restores 100% feasibility | `A1.csv`: 30/30 feasible runs; 0 failed runs | Difference non-sig vs A5 physical ($p=0.715$) | Decisive | Restored without representation change | **VERIFIED** |
| **C3** | Deterministic repair restores feasibility but reduces diversity | `A2.csv`: 100% feasibility, diversity collapses to $5.75$ | Diversity ratio $189.54 / 5.75 = 33.0\times$ | Decisive | Greedy repair collapses exploration | **VERIFIED** |
| **C4** | Q-bit representation preserves diversity beyond repair | `A4.csv`: diversity = $189.54$, 100% feasibility | Maintained across 30 seeds | Strong | Probabilistic sampling preserves diversity | **VERIFIED** |
| **C5** | A5 improves Pareto hypervolume over NSGA-III | `A5.csv` vs `NSGA3.csv`: $247.11\text{M}$ vs $150.67\text{M}$ | $+64.0\%$ relative improvement | Strong | Identical reference point and evaluator | **VERIFIED** |
| **C6** | A5 achieves exact optimum on small-scale instance | `small_exact.csv`: $4.5203$ (phys) / $4.5203$ (pen) | Zero schedule delay vs grid delay ($873.23$) | Qualified | True on penalized fitness; $+39.6\%$ on pure phys | **QUALIFIED** |
| **C7** | A5 is faster than DE at $D=600$ in this implementation | `scalability.csv`: $1.69\text{ s}$ vs $4.49\text{ s}$ ($2.67\times$) | Consistent across $1,000$ evaluations | Strong | Implementation vectorization in Python | **VERIFIED** |
| **C8** | A5 is universally superior to Differential Evolution | `statistics.csv`: Total objective $3.45$ vs $3,976.19$ | Sig on penalty ($p < 1e-5$); comparable on phys ($3.45$ vs $3.70$) | Weak | DE achieved 100% feasibility; scalar winner | **DOWNGRADED** |
| **C9** | A5 provides defensible system integration novelty | `PHASE5_NOVELTY_AUDIT.md`: Prior art matrix | First assembled telemetry-calibrated QI fleet tool | Moderate | Valid at system architecture level | **VERIFIED** |
| **C10** | Egreen Quanta is the first maritime fleet optimizer | Commercial tools exist (ABB OCTOPUS, DNV Nauticus) | Exaggerated absolute claim | None | False claim; prior commercial tools exist | **REJECTED** |
| **C11** | A5 demonstrates quantum advantage | No quantum hardware utilized; classical simulation | Standard classical CPU run | None | False claim; no quantum speedup | **REJECTED** |
| **C12** | Egreen Quanta utilizes quantum computing | Runs on CPython 3.14 on Intel x86 CPU | No physical qubits | None | Scientifically inaccurate term | **REJECTED** |
| **C13** | Canonical QPSO is fundamentally defective | A1 proved Deb's rule cures QPSO entirely | QPSO succeeds with correct comparator | None | False generalization; failure was penalty design | **REJECTED** |
| **C14** | Failure caused by mixed variables + penalty inversion | Trajectory analysis: $\$51\text{k}$ infeas vs $\$109\text{k}$ delay | $100\%$ of failures = assignment collisions | Decisive | Proven by trajectory forensics | **VERIFIED** |
| **C15** | A5 provides practical decision support for green fleets | Multi-objective fuel vs cost vs CII ratings | 30 non-dominated Pareto solutions discovered | Decisive | Practical operational relevance | **VERIFIED** |

---

## 2. Summary of Claim Reconciliation

- **Verified Claims:** 9 claims (C1, C2, C3, C4, C5, C7, C9, C14, C15) are fully supported by reproducible data.
- **Qualified Claims:** 2 claims (C6, C8) require precise formulation boundaries (distinguishing penalized vs. pure physical fitness).
- **Rejected Claims:** 4 claims (C10, C11, C12, C13) are strictly rejected and banned from all presentations.
