# Slide 14: Jury Defense Key Themes & Quick Reference

## Core Defense Strategy for SIH Jury Questions

| Jury Question Theme | Core Defensible Answer | Grounded Quantitative Evidence |
|:--------------------|:-----------------------|:-------------------------------|
| **"Why Quantum-Inspired?"** | Classical probabilistic search metaheuristic; evaluated for exploration diversity against classical controls. No quantum hardware claimed. | Wilcoxon $p = 0.684$ (parity with GA); $+44.7\%$ population bit-entropy diversity ($H = 0.2814$ vs $0.2104$). |
| **"What is Novel?"** | System-level integration of physics guards, quantum-inspired search, conformal uncertainty, and fleet optimization in one reproducible workflow. | 10 automated release gates passing in $1.82\text{s}$; 150/150 pytest tests passing cleanly. |
| **"Are Green Fuels Measured?"** | No. Green fuels are thermodynamic scenario simulations using invariant shaft work ($E = P_B \cdot t$). | Explicitly labeled as "Scenario Estimate" in UI and reports. |
| **"What Failed?"** | Direct Matrix Product State (MPS) tensor network prediction suffered severe numerical divergence and was excluded from serving. | Documented as an honest negative finding in `docs/limitations.md`. |
| **"Is it Autonomous?"** | No. Strictly human-in-the-loop decision support for ship masters and fleet schedulers. | Lacks maritime classification Type Approval; clear advisory warnings on all outputs. |
| **"How Accurate is Uncertainty?"** | Split conformal prediction guarantees distribution-free coverage above the nominal 90% floor. | Empirical coverage: $93.56\%$ (QI-C1); interval width $31.17\%$ narrower than baseline ($1,564.93\text{ kg/h}$). |
| **"Can it Handle Extreme Storms?"** | OOD guard calculates envelope distance $d_{\text{env}}$, warns at $d > 1.0$, and safely intercepts severe states. | $0.0\%$ False Positive Rate on real test data; $96.55\%$ recall on severe synthetic storm states. |
| **"Is it Reproducible?"** | Completely reproducible via a single command with cryptographic artifact verification. | `python reproduce_release.py` runs all gates deterministically in under 2 seconds. |

---

*For the complete 45-question detailed technical breakdown, refer to `presentation/jury_questions.md`.*
