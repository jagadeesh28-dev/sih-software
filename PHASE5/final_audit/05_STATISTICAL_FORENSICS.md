# AUDIT #5: STATISTICAL FORENSICS & RECALCULATION AUDIT
**Project:** SIH26138 — Egreen Quanta  
**Audit Section:** §7 Statistical Forensics & Hypothesis Testing  
**Auditors:** Statistical Methods Auditor & Senior Optimization Research Scientist  
**Date:** September 15, 2026  

---

## 1. Executive Summary & Verification Standard

All statistical claims, hypothesis tests, p-values, effect sizes, Hodges-Lehmann location shifts, and bootstrap confidence intervals reported in Phase 5 were independently recomputed directly from the 30 raw per-seed result CSV files (`PHASE5/results/*.csv`).

### Core Audit Findings:
1. **Omnibus Non-Parametric Significance Confirmed:**  
   The Friedman omnibus test across all 11 algorithms yielded:
   $$\chi^2_F = 188.6414, \quad p = 3.75 \times 10^{-35}$$
   Confirming highly significant differences across the benchmark panel.
2. **Physical Fitness Omnibus Test:**  
   When restricted strictly to the 5 algorithms with 100% feasibility (A1, A2, A4, A5, DE) on pure physical fuel loss:
   $$\chi^2_{F, \text{phys}} = 64.2400, \quad p = 3.72 \times 10^{-13}$$
3. **Statistical Integrity of A5 vs. DE:**  
   On total penalized objective, A5 demonstrated a statistically significant advantage over DE (Wilcoxon $p = 5.59 \times 10^{-9}$, Permutation $p < 10^{-5}$, HL diff = $-1,289.63$, Bootstrap 95% CI: $[-6,712.27, -1,642.96]$). However, this difference is driven by occasional soft penalty incursions in DE; on pure physical fuel loss, A5 ($3.45$) and DE ($3.70$) are closely matched.
4. **Bootstrap CI Consistency Check:**  
   All bootstrap 95% confidence intervals satisfy the mathematical requirement $\text{CI}_{\text{lower}} < \text{CI}_{\text{upper}}$ and accurately bound the sample mean difference.

---

## 2. Independent Statistical Recalculation Table

Recomputed using 100,000 paired sign-flip permutation resamples and 10,000 paired bootstrap resamples:

| Pairwise Comparison | Mean Diff ($\Delta$) | Wilcoxon $W$-stat | Wilcoxon $p$-value | Permutation $p$ (100k) | Rank-Biserial $r$ | Hodges-Lehmann Diff | Bootstrap 95% CI | Significance ($\alpha=0.01$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **A5 vs. A0** | $-12,199.22$ | $193.0$ | $0.58376$ | $0.00399$ | $-0.1183$ | $-9,999.60$ | $[-19,665.42, -5,399.67]$ | Non-Sig (Holm) |
| **A5 vs. A1** | $-1,999.91$ | $215.0$ | $0.71513$ | $0.13056$ | $+0.0796$ | $+0.01$ | $[-5,333.04, +0.01]$ | Non-Sig |
| **A5 vs. DE** | $-3,972.74$ | $2.0$ | $5.59 \times 10^{-9}$ | $< 10^{-5}$ | $-0.9914$ | $-1,289.63$ | $[-6,712.27, -1,642.96]$ | **SIGNIFICANT** |
| **A5 vs. PSO** | $-30,164.55$ | $14.0$ | $2.05 \times 10^{-7}$ | $< 10^{-5}$ | $-0.9398$ | $-25,498.41$ | $[-37,997.47, -22,031.79]$ | **SIGNIFICANT** |
| **A5 vs. GA** | $-27,722.85$ | $1.0$ | $3.73 \times 10^{-9}$ | $< 10^{-5}$ | $-0.9957$ | $-25,499.45$ | $[-36,532.37, -19,448.33]$ | **SIGNIFICANT** |
| **A5 vs. Random**| $-28,678.53$ | $0.0$ | $1.86 \times 10^{-9}$ | $< 10^{-5}$ | $-1.0000$ | $-29,367.61$ | $[-32,678.47, -24,504.49]$ | **SIGNIFICANT** |
| **DE vs. A0** | $-8,226.48$ | $232.0$ | $1.00000$ | $0.04288$ | $+0.0022$ | $+0.02$ | $[-15,866.09, -1,108.56]$ | Non-Sig (Holm) |

---

## 3. Methodological Notes on Non-Parametric Tests

### 3.1 Why Wilcoxon $p = 0.584$ for A5 vs. A0 while Permutation $p = 0.00399$
This subtle phenomenon is an excellent example of rank-based vs. mean-based testing in constrained optimization:
- On the **24 feasible runs**, A0 and A5 both achieved near-optimal solutions ($3.38$ vs. $3.45$). In 13 of those 24 runs, A0 had a negligible numerical advantage ($|\Delta| < 0.07$), yielding small positive differences.
- On the **6 failed runs**, A0 incurred massive penalties ($\$50,000$), creating 6 massive negative differences.
- The Wilcoxon signed-rank test ranks differences by absolute magnitude. The 6 massive ranks are negative, but the 24 smaller ranks are evenly split, yielding a two-sided Wilcoxon $p = 0.584$.
- The permutation test evaluates the **raw mean difference** ($-12,199.22$), which is heavily influenced by the 6 catastrophic failures, yielding $p = 0.00399$.
- Both tests are mathematically correct; the report must explain that A0's average degradation is caused by severe constraint failures rather than smooth performance decay.

### 3.2 Tie Handling & Floating-Point Threshold
A threshold of $|\Delta J| \le 10^{-5}$ was enforced. Zero differences were treated using Pratt's method, which retains zeros in rank assignments.

---

## 4. Audit Verdict: PASS
All reported statistics are mathematically verified, reproducible, and supported by the raw per-seed benchmark data.
