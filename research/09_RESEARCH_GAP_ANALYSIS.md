# 09 — RESEARCH GAP ANALYSIS
## RQ11–RQ13: Is There a Genuine Contribution Beyond Prior Art?

---

## 1. Gap Identification Methodology

This section follows the standard academic gap analysis process:
1. Map existing literature to a feature matrix
2. Identify combinations absent from literature
3. Assess whether the absent combination is non-trivially novel
4. Test the novelty claim against "obvious" extensions

---

## 2. The Feature Combination Matrix

We categorize all relevant papers (established in §05) by the features they address:

| Feature | Han 2023 (QGA) | Fraunhofer CML | Aviation FAP | VRP-QIEA | Phase 4 Baseline |
|:---|:---:|:---:|:---:|:---:|:---:|
| QI algorithm | ✅ | ✅ | ✅ | ✅ | ✅ |
| Multi-vessel | ❌ | ✅ | ✅ | ✅ | ✅ |
| Heterogeneous types | ❌ | ⚠️ | ✅ | ❌ | ✅ |
| Speed optimization | ✅ | ❌ | ❌ | ❌ | ✅ |
| Fuel type categorical | ❌ | ❌ | ❌ | ❌ | ✅ |
| Alternative fuels | ❌ | ❌ | ❌ | ❌ | ✅ |
| IMO CII | ✅ | ❌ | ❌ | ❌ | ✅ |
| FuelEU Maritime | ❌ | ❌ | ❌ | ❌ | ✅ |
| Demand assignment | ❌ | ❌ | ✅ | ✅ | ✅ |
| Shore power | ❌ | ❌ | ❌ | ❌ | ✅ |
| Weather CVaR | ❌ | ❌ | ❌ | ❌ | ✅ |
| Real telemetry | ❌ | ❌ | ❌ | ❌ | ✅ |
| Heterogeneous QI rep | ❌ | ❌ | ❌ | ❌ | ❌ |
| Feasibility-first CHT | ❌ | ❌ | ✅ | ✅ | ❌ |
| Statistical rigor | ❌ | ❌ | ✅ | ⚠️ | ✅ |

**Key observation:** No single paper or combination of papers covers the full feature set that SIH26138 addresses. The "Heterogeneous QI representation" row is empty across all prior art — this is the core novel claim.

---

## 3. What Does "Heterogeneous QI Representation" Mean?

A unified representation that simultaneously encodes:
- **Q-bit binary observation** for demand assignment and shore power
- **Categorical probability vector (Dirichlet-Q)** for fuel mode
- **Quantum-potential well search** for continuous speed

within a single **integrated probabilistic framework** where:
1. The update rules are derived from quantum-inspired principles (not ad hoc)
2. All variable types interact through a shared fitness function
3. Constraints are enforced at the representation level, not post-hoc

**This combination has not been published for any transportation optimization problem.** Individual components exist; the integration does not.

---

## 4. Is the Combination Trivially Obvious?

**Test 1: Is QPSO + QIEA combination explicitly described in prior art?**  
Search result: No published paper describes a joint QPSO-QIEA framework where:
- QIEA handles binary/categorical variables
- QPSO handles continuous variables
- The two components share a fitness function and are jointly trained

Several papers combine QPSO with GA or DE, but not with QIEA. Evidence Class A (confirmed by systematic search).

**Test 2: Is the maritime context obvious enough to be a "trivial extension"?**  
The maritime context introduces non-obvious technical challenges:
- Port-fuel compatibility creates constraint coupling across fleet decisions
- FuelEU Maritime's fleet-wide GHG constraint links all vessels' fuel choices
- Methane slip modeling changes the GHG accounting for LNG vessels depending on engine type and speed
- Real telemetry calibration introduces surrogate uncertainty that affects optimization convergence

These are non-obvious domain-specific challenges. Evidence Class A.

**Test 3: Is QIEA's categorical representation "just one-hot encoding"?**  
No. The Dirichlet-Q (categorical probability vector) update rule:
$$p_k' = p_k + \eta \cdot \mathbb{1}[\hat{f}_{best} = k] - \lambda \cdot p_k$$
maintains a probability distribution over categories, preserving diversity that static one-hot encoding discards. The update is derived from the QIEA rotation gate principle extended to categorical spaces. This derivation is non-trivial.

**Test 4: Does the "Novelty-by-Combination" standard hold?**  
Academic novelty by combination requires:
1. The combination has not been published (confirmed by gap matrix)
2. Combining the elements produces something not predictable from the parts (the joint heterogeneous representation with feasibility-first is not predictable from QPSO alone or QIEA alone)
3. The combination has practical value (confirmed by Phase 4.1 analysis: fixing QPSO's representation defect is the critical engineering challenge)

All three criteria are satisfied.

---

## 5. What We Cannot Claim

**We CANNOT claim:**
1. That Hybrid QI-HFO will outperform DE in objective quality — Phase 4 shows DE is competitive; DE's feasibility advantage disappears if QPSO is fixed; the comparison against a hybrid remains an open empirical question
2. That QPSO is definitively inferior — it is an implementation defect, not an algorithmic one
3. That QI algorithms are "quantum" in the sense of quantum computing — they are classical algorithms inspired by quantum mechanical principles
4. That the research gap is large — it is narrow, and honest acknowledgment of this strengthens the scientific contribution
5. That our benchmark is universally applicable — it is specific to the SIH26138 problem formulation

---

## 6. Honest Risk Assessment

| Risk | Probability | Impact | Mitigation |
|:---|:---:|:---:|:---|
| A paper we missed covers the gap | Low | High | Systematic search; disclosure in paper |
| Hybrid doesn't outperform DE | Medium | Low | Negative results are acceptable |
| Hybrid is hard to implement correctly | Medium | Medium | Phase 5 incremental build |
| Maritime practitioner validation missing | High | Medium | Phase 5 sensitivity study |
| Statistical power insufficient (n=30) | Low | Medium | Phase 5 can increase n |

---

## 7. Research Gap Summary (Final)

The genuine, narrow, and defensible research gap for SIH26138 is:

> **"Heterogeneous Quantum-Inspired Representation for Constrained Maritime Fleet Optimization under Regulatory and Fuel-Diversity Uncertainty"**

This encompasses:
1. First application of QIEA-derived categorical probability vector to maritime fuel mode optimization
2. First unified QI framework (binary Q-bit + categorical Q-vector + continuous quantum well) for fleet-level assignment, fuel, and speed
3. First integration of FuelEU Maritime 2025 constraints into a QI-based optimizer
4. First real-telemetry surrogate-calibrated QI optimizer for heterogeneous maritime fleet

The combination is non-trivially novel (Test 1–4 above), publishable (suitable venues identified in §05), and practically motivated by the Phase 4.1 forensic audit.
