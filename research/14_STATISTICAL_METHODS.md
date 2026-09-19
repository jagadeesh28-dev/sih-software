# 14 — STATISTICAL METHODS: DETAILED JUSTIFICATION
## RQ19: Are the Statistical Tests Valid and Sufficient?

---

## 1. Phase 4 Statistical Test Inventory

| Test | Purpose | Applied To | Justification |
|:---|:---|:---|:---|
| Wilcoxon rank-sum | Primary algorithm comparison | Objective value over 30 seeds | Non-parametric; no normality assumption |
| Holm-Bonferroni | FWER correction | All 9 pairwise claims | Controls family-wise error rate |
| Hodges-Lehmann | Effect size | Primary comparison | Robust location-shift estimator |
| BCa bootstrap | Confidence interval | Hodges-Lehmann Δ | Bias-corrected, acceleration-corrected |
| Shapiro-Wilk | Normality check | Pre-test for objective values | Justifies Wilcoxon choice |
| Binomial exact | Feasibility rate CI | 26/30 feasibility | Exact method; small sample |
| Clopper-Pearson | Feasibility rate CI | Same | Standard exact binomial CI |

---

## 2. Why Wilcoxon Rank-Sum (Not t-test)

**Shapiro-Wilk pre-test:** Phase 4 objective distributions for both QPSO and DE showed significant non-normality (p < 0.05 Shapiro-Wilk on raw objectives). This justifies the use of Wilcoxon over a paired/two-sample t-test.

**Wilcoxon rank-sum (Mann-Whitney U):** Tests whether one distribution is stochastically larger than another. Does not assume normality. Valid for any continuous distribution.

**Common misconception:** Wilcoxon does NOT test means. It tests the probability that a randomly selected observation from group A exceeds one from group B. Correct interpretation: $P(X_A > X_B) \neq 0.5$ vs. null hypothesis of equal distributions.

---

## 3. FWER Correction: Holm-Bonferroni

**Why FWER correction is necessary:** With 9 statistical claims in Phase 4, testing each at $\alpha = 0.05$ would lead to:
$$P(\text{at least one false positive}) = 1 - (1-0.05)^9 = 36.9\%$$

This is unacceptable for scientific publication.

**Holm-Bonferroni procedure:**
1. Order p-values: $p_{(1)} \leq p_{(2)} \leq \cdots \leq p_{(k)}$
2. For $i = 1, 2, \ldots, k$: reject $H_{(i)}$ if $p_{(i)} \leq \frac{\alpha}{k-i+1}$
3. Stop at first non-rejection; all subsequent hypotheses retained

**Result (Phase 4):** After Holm-Bonferroni correction, the primary claim (QPSO ≈ DE in objective quality among feasible) was confirmed at adjusted $\alpha = 0.05$. The feasibility difference remained significant.

---

## 4. Effect Size: Hodges-Lehmann Estimator

**Why effect size matters:** Statistical significance (p-value) depends on sample size. A significant p-value with large $n$ may correspond to a practically meaningless difference.

**Hodges-Lehmann estimator:**
$$\hat{\Delta} = \text{median}\{X_{A,i} - X_{B,j} : i = 1,\ldots,n_A; j = 1,\ldots,n_B\}$$

This is the median of all $n_A \times n_B = 30 \times 30 = 900$ pairwise differences.

**Phase 4 Result:** $\hat{\Delta} = -\$241$ (QPSO objective minus DE objective). The 95% BCa CI was $[-\$1{,}847, +\$1{,}124]$. Since the CI spans zero, we cannot conclude either algorithm is definitively better.

**Interpretation:** QPSO and DE have statistically equivalent objective quality on feasible solutions. This is a **correct negative result** and is scientifically valid.

---

## 5. Bootstrap Confidence Intervals

**BCa Bootstrap (Bias-Corrected and Accelerated):**

Standard percentile bootstrap may have coverage problems (actual CI coverage $\neq$ nominal 95%) for skewed distributions. BCa corrects for:
- **Bias:** The bootstrap distribution may be centered away from the true estimator
- **Acceleration:** The standard error of the estimator may vary with the parameter value

**Procedure:**
1. Draw 10,000 bootstrap samples from the data
2. Compute $\hat{\Delta}$ for each sample
3. Apply BCa correction (compute $z_0$ and $a$ parameters)
4. Report BCa CI endpoints

**Phase 4:** Used `scipy.stats.bootstrap` with `method='BCa'`, $n_{boot} = 10{,}000$. This is state-of-the-art and appropriate for our sample size of $n = 30$.

---

## 6. What Phase 5 Statistics Should Add

| New Test | Justification |
|:---|:---|
| Kruskal-Wallis (3+ algorithms) | When comparing QPSO vs. DE vs. Hybrid simultaneously |
| Dunn's post-hoc with Holm | Pairwise comparison after Kruskal-Wallis |
| One-tailed Wilcoxon | For directional hypotheses: "Hybrid ≥ QPSO in feasibility" |
| Brown-Forsythe (variance) | Test if algorithms differ in variance (robustness) |
| Cliff's delta | Non-parametric effect size as alternative to Hodges-Lehmann |
| Convergence speed tests | Wilcoxon on "generation of first feasible" as secondary metric |

---

## 7. Minimum Defensible Sample Size

For Wilcoxon at $\alpha = 0.05$, power = 0.80, and a medium effect size (Cohen's d ≈ 0.5):
- Required sample size: $n \approx 25$ per group

Our $n = 30$ per algorithm satisfies this requirement. For detecting small effects (d ≈ 0.2), $n \approx 200$ would be needed — outside our scope.

**Recommendation:** Maintain $n = 30$ seeds for Phase 5. This is standard practice in metaheuristic optimization benchmarking (see CEC Competition Guidelines, SEAL benchmarking guidelines).

---

## 8. False Claims to Avoid

| Claim | Status | Why Not |
|:---|:---|:---|
| "Hybrid QI-HFO is significantly better than DE" | ❌ Premature | Not yet benchmarked; no data |
| "QPSO is fundamentally flawed" | ❌ Wrong | Representation + CHT defect, not inherent |
| "QI algorithms are quantum" | ❌ Misleading | Classical algorithms; quantum-inspired label only |
| "Phase 4 shows DE is superior" | ❌ Incomplete | DE is superior in feasibility; equivalent in objective |
| "30 seeds is sufficient for all claims" | ⚠️ Conditional | Sufficient for medium effects; not for small effects |
