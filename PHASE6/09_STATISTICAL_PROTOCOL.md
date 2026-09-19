# PHASE 6 — STEP 9: STATISTICAL TESTING & PRACTICAL SIGNIFICANCE PROTOCOL
## SIH26138 — Egreen Quanta
### 30-Seed Matched Inferential Statistics, Hypothesis Testing, and Effect Size Analysis

**Date:** September 19, 2026  
**Auditor:** Statistical Experimentalist, Lead ML Research Scientist  
**Sample Size:** $N = 30$ matched random seeds (Seeds: 42, 1001–1029)  
**Primary Test:** Non-parametric two-sided paired Wilcoxon signed-rank test  
**Multiple Testing Correction:** Step-down Holm-Bonferroni family-wise error rate control ($\alpha = 0.05$)  

---

## 1. Practical Significance vs. Statistical Significance Thresholds

In high-sample-size time-series benchmarks, tiny marginal improvements can achieve $p < 0.05$ while offering zero meaningful operational utility. 
Before inspecting test statistics, strict practical engineering thresholds were established:

| Evaluation Metric | Minimum Practical Significance Threshold ($\Delta_{practical}$) | Justification / Operational Grounding |
| :--- | :--- | :--- |
| **Fuel Mass Flow MAE** | **$\ge 15.0\text{ kg/h}$ ($>6.0\%$ relative reduction)** | Flow meter measurement noise floor is $\pm 0.5\%$; a reduction $<15\text{ kg/h}$ is indistinguishable from sensor calibration drift. |
| **Percentage Error (MAPE)**| **$\ge 1.0\%$ absolute drop** | Operational charter party disputes require $>1.0\%$ verified difference. |
| **Inference Latency** | **$\le 1.0\text{ ms}$ per observation** | Digital twin deployment on shipboard edge hardware requires real-time telemetry processing ($>1,000\text{ Hz}$). |
| **Memory Footprint** | **$\le 100\text{ MB}$ peak allocation** | Containerized deployment on low-power embedded maritime gateways. |
| **Physical Violations** | **$0$ negative predictions** | Maritime fuel mass flow is strictly non-negative; zero violations tolerated. |

---

## 2. Inferential Statistical Test Results (Across 30 Matched Seeds)

Every candidate model was evaluated under the exact same 30 random seeds against the frozen reference baseline **P2 (Physics + ML Residual)**:

| Model Candidate | Comparison Against P2 | Test MAE Mean $\pm$ Std (kg/h) | Median Test MAE (kg/h) | 95% Bootstrap Confidence Interval | Raw Wilcoxon $p$-value | Holm-Bonferroni Adjusted $p$ | Rank-Biserial Effect Size ($r$) | Hodges-Lehmann Median Difference | Practical Significance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **P1 (Pure Classical ML)** | P1 vs P2 Baseline | $257.18 \pm 0.74$ | 257.15 | $[256.91, 257.45]$ | $1.73 \times 10^{-6}$ | $6.92 \times 10^{-6}$ | $+1.00$ (Large Deficit) | $+8.93\text{ kg/h}$ (Worse) | **P2 Superior** |
| **P2 (Physics + ML Residual)**| **Baseline Reference** | **$248.12 \pm 0.81$** | **248.09** | **$[247.83, 248.42]$** | **Reference** | **Reference** | **0.00** | **$0.00\text{ kg/h}$** | **Baseline** |
| **P3 (Classical GA-FS + ML)** | P3 vs P2 Baseline | $237.24 \pm 7.47$ | 235.69 | $[234.50, 239.90]$ | $2.84 \times 10^{-5}$ | $8.52 \times 10^{-5}$ | $-0.88$ (Strong Win) | $-10.87\text{ kg/h}$ | Statistically Sig, Marginal Practical |
| **P4 (QI-C1: QIEA-FS + ML)** | P4 vs P2 Baseline | $237.96 \pm 5.46$ | 236.42 | $[236.00, 239.95]$ | $3.12 \times 10^{-5}$ | $8.52 \times 10^{-5}$ | $-0.85$ (Strong Win) | $-10.28\text{ kg/h}$ | Statistically Sig, Marginal Practical |
| **P5 (QI-C1: QIEA + QPSO)** | P5 vs P2 Baseline | $242.95 \pm 5.12$ | 242.80 | $[241.10, 244.80]$ | $1.85 \times 10^{-3}$ | $3.70 \times 10^{-3}$ | $-0.62$ (Moderate Win) | $-5.21\text{ kg/h}$ | Below Practical Threshold |
| **P6 (QI-C2: MPS Tensor Net)**| P6 vs P2 Baseline | $2.25 \times 10^{12} \pm 3.36 \times 10^{12}$ | $1.60 \times 10^{11}$ | $[1.12 \times 10^{12}, 3.51 \times 10^{12}]$ | $1.73 \times 10^{-6}$ | $6.92 \times 10^{-6}$ | $+1.00$ (Severe Deficit)| $+1.69 \times 10^{12}\text{ kg/h}$ | **QI Failed** |
| **P7 (QI Ensemble)** | P7 vs P2 Baseline | $238.31 \pm 3.82$ | 237.50 | $[236.90, 239.70]$ | $2.95 \times 10^{-5}$ | $8.52 \times 10^{-5}$ | $-0.87$ (Strong Win) | $-10.09\text{ kg/h}$ | Statistically Sig, Marginal Practical |

---

## 3. Direct Head-to-Head: QIEA (P4) vs. Classical GA (P3)

To isolate whether the quantum-inspired mechanism itself is causal, we perform a direct paired test between **P4 (QIEA-FS)** and **P3 (Classical GA-FS)**:
- Mean MAE Difference ($\text{P4} - \text{P3}$): $+0.72\text{ kg/h}$ ($237.96$ vs $237.24$)
- Paired Wilcoxon $p$-value: $p = 0.684$ (**Not Statistically Significant**)
- Hodges-Lehmann Difference: $+0.65\text{ kg/h}$ (95% CI: $[-1.85, +3.12]$)
- Rank-Biserial Correlation: $r = +0.08$ (Negligible effect size)

### Key Scientific Verdict:
QIEA feature selection is **statistically comparable** to Classical Genetic Algorithm feature selection ($p = 0.684$). 
The quantum-inspired Q-bit mechanism does **NOT** provide a statistically superior prediction accuracy over a budget-matched classical genetic algorithm. 
However, as demonstrated in Step 19/20, QIEA preserves significantly higher exploratory population entropy ($H(Q) = 0.2814$ vs $0.1945$) and avoids premature convergence.

---

## 4. Tensor Network / MPS Divergence Analysis (P6)

The direct quantum-inspired candidate **QI-C2-MPS** suffered numerical gradient instability across 20 out of 30 seeds, with median MAE exploding to $1.60 \times 10^{11}\text{ kg/h}$.
Even on its single best seed (Seed 1006), the MPS model achieved $\text{MAE} = 1,196.93\text{ kg/h}$, trailing far behind the classical baseline ($246.97\text{ kg/h}$) and the matched classical polynomial regression model ($275.13\text{ kg/h}$).

**Scientific Verdict on Candidate QI-C2:**
The claim that a direct Matrix Product State (MPS) tensor network provides superior maritime fuel prediction is **EMPIRICALLY DISPROVEN**. Unconstrained stochastic gradient descent on deep tensor train chains without gauge-fixing orthogonalization is unsuited for tabular maritime telemetry.
