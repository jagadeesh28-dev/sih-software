# 20 — EVIDENCE LEDGER
## Complete Evidence Catalog for All Research Claims

---

## Evidence Classification

- **Class A:** Direct peer-reviewed academic evidence, verified by systematic search
- **Class B:** Industry/grey literature, pilot studies, conference proceedings (not fully peer-reviewed)
- **Class C:** Indirect evidence, inference from related work, expert reasoning

---

## Claim-Evidence Matrix

| Claim ID | Claim Statement | Evidence Source | Class | Strength |
|:---|:---|:---|:---:|:---:|
| **E01** | QPSO designed for continuous spaces only (Sun & Xu 2004) | Sun, Xu, Fang & Feng, CEC 2004 | A | Strong |
| **E02** | Standard QPSO struggles with categorical variables | ResearchGate, MDPI, arXiv (2020–2024) | A | Strong |
| **E03** | QPSO achieves 86.67% feasibility on Phase 4 benchmark | Phase 4 experiment data, 30 seeds | A | Strong |
| **E04** | DE achieves 100% feasibility on Phase 4 benchmark | Phase 4 experiment data, 30 seeds | A | Strong |
| **E05** | Penalty Inversion is the primary QPSO failure cause | Phase 4.1 Claim Ledger, Claim B | A | Strong |
| **E06** | Wilcoxon p=0.23 (NS): QPSO ≈ DE in feasible objective quality | Phase 4 statistical analysis | A | Strong |
| **E07** | QIEA naturally handles binary variables (Han & Kim 2002) | Han, Kim, IEEE TEC 2002 | A | Strong |
| **E08** | QIEA convergence proof exists under mild conditions | Han, Kim, IEEE TEC 2002 | A | Strong |
| **E09** | QGA applied to maritime speed optimization (Han et al. 2023) | Han, Ma, Ma, JCP 2023 | A | Strong |
| **E10** | No published paper combines QIEA+QPSO for maritime fleet | Systematic search (2012–2026) | A | Medium |
| **E11** | Deb's feasibility rule eliminates penalty inversion | Deb 2000, CMAME | A | Strong |
| **E12** | QUBO approach used for maritime scheduling (Fraunhofer CML) | Fraunhofer CML reports | B | Medium |
| **E13** | Commercial systems (Wärtsilä, Kongsberg, ABB) do not use QI | Company documentation | B | Strong |
| **E14** | No patents cover QI + maritime fleet + CII + alternative fuels | Google Patents, WIPO, Espacenet | A | Strong |
| **E15** | QIDE provides Q-bit diversity for discrete problems (2022–2024 literature) | arXiv, MDPI comparative studies | A | Medium |
| **E16** | FuelEU Maritime GHG intensity limit active from 2025 | EU Regulation 2023/1805 | A | Strong |
| **E17** | IMO 2023 GHG Strategy sets 2030/2040/2050 targets | IMO Resolution MEPC.377(80) | A | Strong |
| **E18** | LNG methane slip: 3.1% well-to-wake (FuelEU Maritime Annex II) | EU Regulation Annex II | A | Strong |
| **E19** | CVaR is industry standard for maritime risk management | Multiple maritime finance papers | B | Medium |
| **E20** | Heterogeneous QI representation (binary+cat+cont) for fleet: no prior art | Systematic search + gap matrix | A | Medium |
| **E21** | Hybrid QI-HFO not yet implemented (as of Phase 4.1) | Phase 4.1 audit scope | A | Strong |
| **E22** | No Free Lunch theorem: no universally superior algorithm | Wolpert & Macready 1997 | A | Strong |
| **E23** | DE's difference-vector mutation provides natural diversity | Standard DE theory | A | Strong |

---

## Disputed or Unverified Claims

| Claim | Status | Required Action |
|:---|:---|:---|
| "Hybrid QI-HFO will achieve 100% feasibility" | ❌ Unverified | Phase 5 experiment needed |
| "Hybrid QI-HFO will match DE in objective quality" | ❌ Unverified | Phase 5 experiment needed |
| "QIEA is superior to QPSO for all mixed-variable problems" | ❌ Overly broad | Do not claim; too broad |
| "QI algorithms are quantum" | ❌ False | Quantum-inspired only |
| "Our approach is deployable on real ships" | ❌ Unverified | Requires operational validation |

---

## Evidence Gaps and Required Future Evidence

| Gap | Action Required |
|:---|:---|
| No peer-reviewed citation for "Hybrid QPSO-QIEA" | Phase 5 will generate this as original contribution |
| No independent replication of Phase 4 results | Share code on GitHub for replication |
| No prospective telemetry validation | Future collaboration with shipping company needed |
| No parameter sensitivity analysis | Phase 5.3 sensitivity study |
| Fraunhofer CML results not peer-reviewed | Cite as B-class evidence only |
