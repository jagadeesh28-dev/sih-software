# 22 — OPEN QUESTIONS & FUTURE DIRECTIONS
## Unresolved Scientific Questions for Phase 5 and Beyond

---

## 1. Empirical Open Questions

These questions can only be answered by running Phase 5 experiments.

### OQ-1: Does the QPSO Patch Achieve 100% Feasibility?

**Hypothesis:** Implementing Deb's rule + dynamic penalty + repair operator will eliminate Penalty Inversion and achieve 100% feasibility on the Phase 4 benchmark.

**Test:** 30-seed benchmark of QPSO-patched vs. QPSO-original.

**If yes:** Confirms that the failure was an implementation defect, not an algorithmic one. Strengthens the argument that QPSO is viable for this problem class.

**If no:** Additional forensic analysis needed. Possible residual causes: (a) penalty is still inverted in edge cases, (b) additional failure modes not identified in Phase 4.1, (c) repair operator introduces new stagnation patterns.

---

### OQ-2: Does Hybrid QI-HFO Match or Exceed DE in Objective Quality?

**Hypothesis:** The hybrid's principled categorical representation will reduce search time on discrete variables, allowing more effective speed optimization within the same evaluation budget.

**Test:** 30-seed benchmark of Hybrid QI-HFO vs. DE vs. QPSO-patched.

**Possible outcomes and their interpretation:**

| Outcome | Interpretation | Action |
|:---|:---|:---|
| Hybrid > DE | QI representation improves optimization | Publish as positive result |
| Hybrid = DE | Both valid; hybrid has design advantage | Publish; emphasize design contribution |
| Hybrid < DE | QI representation adds overhead without benefit | Publish as honest negative result; analyze why |

**No outcome is "bad" from a scientific perspective.** The contribution is in the systematic comparison and principled design, not in claiming superiority.

---

### OQ-3: Does the Hybrid Scale with Fleet Size?

**Hypothesis:** QIEA's Q-bit representation should scale better than QPSO for increasing fleet size (more categorical variables), because Q-bit diversity grows multiplicatively while QPSO's categorical plateau problem worsens.

**Test:** Scaling study at V = 4, 6, 8, 12 vessels (with proportionally scaled demand).

**Metric:** Feasibility rate and objective gap as function of V.

---

### OQ-4: What Is the Minimum Evaluation Budget for the Hybrid?

**Hypothesis:** The hybrid's conditional observation mechanism eliminates infeasible evaluations, effectively improving per-evaluation quality. It may converge in fewer evaluations than QPSO or DE.

**Test:** Convergence speed study (objective vs. evaluation count) for all algorithms.

---

## 2. Theoretical Open Questions

### OQ-5: Convergence Proof for Hybrid QI-HFO

**Status:** No convergence proof exists for the proposed hybrid.

**What is needed:** Proof (or disproof) that the joint QIEA-QPSO update with Deb's rule and conditional observation converges to a global optimum with probability 1 under ergodic conditions.

**Difficulty:** High. QIEA convergence is proven for binary problems (Han & Kim 2002). QPSO convergence is proven for continuous problems (Sun 2004 + extensions). The joint convergence is an open theoretical question.

**Interim approach:** Empirical convergence (Phase 5 experiments) is sufficient for SIH 2026. Theoretical convergence is a future research question.

---

### OQ-6: Optimal Rotation Angle for Categorical Q-Vectors

**Status:** The Dirichlet-Q rotation angle (equivalent to QIEA rotation step $\delta$) is proposed as $\delta = 0.05\pi$ following Han & Kim (2002) binary convention. The optimal value for categorical probability vectors is unknown.

**What is needed:** Parameter study on $\delta$ for categorical Q-vectors; possible derivation from information-theoretic principles.

---

### OQ-7: Information-Theoretic Justification for Q-bit Representation

**Status:** QIEA's Q-bit representation is heuristically motivated by quantum mechanics. A rigorous information-theoretic justification (e.g., showing that Q-bit representation maximizes entropy at initialization and minimizes relative entropy toward the optimal distribution) would strengthen the theoretical foundation.

**Difficulty:** Medium. Related to estimation of distribution algorithm (EDA) literature.

---

## 3. Application Open Questions

### OQ-8: Real-World Deployment Under Operational Constraints

**Status:** Our benchmark uses a simplified operational model. Real-world deployment requires:
- Multi-port routing (not single port)
- Charter party speed warranties (contractual speed obligations)
- Emergency response provisions
- Dynamic replanning as weather/demand changes

**Research question:** How does Hybrid QI-HFO perform under dynamic replanning (rolling horizon optimization)?

### OQ-9: Integration with Commercial Maritime Management Systems

**Status:** Wärtsilä, Kongsberg, ABB have proprietary APIs for vessel data. Integration with these systems would require partnerships.

**Research question:** Is Hybrid QI-HFO's decision quality better than or complementary to commercial systems when given identical data?

---

## 4. Priority Order for Phase 5

1. **OQ-1** (QPSO patch feasibility) — must resolve before proceeding
2. **OQ-2** (Hybrid vs. DE benchmark) — primary Phase 5 contribution
3. **OQ-3** (scaling study) — strengthens generalizability claims
4. **OQ-4** (evaluation budget convergence) — useful for practical deployment
5. **OQ-6** (categorical rotation angle) — parameter study, lower priority
6. **OQ-5, OQ-7** (theoretical questions) — future research, not Phase 5 scope
7. **OQ-8, OQ-9** (deployment) — Phase 6+ scope
