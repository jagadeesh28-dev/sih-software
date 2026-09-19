# AUDIT #13: NOVELTY CLAIMS & INTELLECTUAL PROPERTY BOUNDARIES
**Project:** SIH26138 — Egreen Quanta  
**Audit Section:** §18 Novelty & Prior Art Review  
**Auditors:** Prior-Art / Novelty Claim Auditor & Patentability Reviewer  
**Date:** September 15, 2026  

---

## 1. Classification of Contributions by Category

To prevent inflated novelty claims during the SIH 2026 Grand Finale, this audit strictly delineates the five categories of scientific contribution:

| Contribution Category | Specific Component in Egreen Quanta | Prior Art Reference | Legal & Scientific Classification | Novelty Status |
| :--- | :--- | :--- | :--- | :--- |
| **1. Algorithmic Novelty** | Delta-potential QPSO equations ($m_{\text{best}}, \beta$) | Sun et al. (2004, *IEEE CEC*) | Established prior art | **NON-NOVEL (Adopted)** |
| **1. Algorithmic Novelty** | Two-state Q-bit $|\psi\rangle$ & rotation gate $R(\Delta\theta)$ | Han & Kim (2002, *IEEE TEVC*) | Established prior art | **NON-NOVEL (Adopted)** |
| **1. Algorithmic Novelty** | Feasibility-first pairwise comparator | Deb (2000, *CMAME*) | Established prior art | **NON-NOVEL (Adopted)** |
| **2. Representation Novelty** | Dirichlet Quantum Probability Vector for multi-fuel choices | Generalization of 2-state Q-bit | Domain-specific adaptation | **INCREMENTAL ADAPTATION** |
| **3. Domain Adaptation** | Bijective Cargo Demand Assignment Decoder | Order-statistic rank sorting | Engineering synthesis | **DOMAIN ADAPTATION** |
| **4. Architectural / System Integration** | Heterogeneous partition coupling discrete Q-bits to continuous QPSO with Deb selection & FuelEU pooling | Targeted search across IEEE, ScienceDirect, USPTO | System-level assembly | **DEFENSIBLE SYSTEM NOVELTY** |
| **5. Experimental Methodology** | Exact A0–A5 ablation isolating constraint handling from quantum mechanics in maritime routing | Established ablation standards | Rigorous benchmark design | **METHODOLOGICAL MERIT** |

---

## 2. Commercial Systems & Patent Boundaries

### 2.1 Commercial System Survey
- **DNV Nauticus / Veracity:** Focuses on MRV emissions reporting, regulatory audits, and post-voyage carbon accounting. Does not perform real-time stochastic metaheuristic fleet dispatch.
- **ABB Ability™ Marine Advisory (OCTOPUS):** Focuses on single-vessel hydrodynamic motion and wave routing. Does not solve multi-vessel combinatorial fleet scheduling or green-fuel pooling.
- **StormGeo BVS:** Weather routing using classical deterministic Dijkstra/MIP heuristics.

### 2.2 Patent Survey (USPTO / EPO)
- Patents such as US 10,853,564 B2 solve maritime fleet deployment using classical Mixed-Integer Linear Programming (MILP).
- Chinese patent CN 112,883,617 A applies single-ship QGA to 2D geometric obstacle avoidance, not multi-vessel fleet scheduling or FuelEU pooling.

---

## 3. Mandatory Presentation Standards & Language Rules

### ❌ Strictly Forbidden Claims (Scientific Misrepresentation):
1. *"We developed a quantum computing algorithm."*
2. *"We achieved quantum supremacy / exponential quantum speedup."*
3. *"We invented Quantum-Behaved Particle Swarm Optimization."*
4. *"This is the first maritime fleet optimization tool in existence."*
5. *"Quantum-inspired mechanics was the sole factor that cured the feasibility failures."*

### ✔ Peer-Review Defensible Statement:
> *"A heterogeneous quantum-inspired optimization framework for maritime green-fleet deployment that matches optimization representation to decision-variable type, combining Q-bit-based probabilistic search for discrete/binary fleet decisions with QPSO for continuous operational variables, supported by feasibility-first constraint handling and uncertainty-aware multi-objective evaluation."*

### ✔ Allowed Prior-Art Disclaimer:
> *"No directly comparable assembled system was identified in the targeted literature, patent, and commercial prior-art search."*

---

## 4. Audit Verdict: PASS (SYSTEM INTEGRATION NOVELTY SUPPORTED)
The intellectual property scope is defensible, honest, and appropriately constrained to architectural integration.
