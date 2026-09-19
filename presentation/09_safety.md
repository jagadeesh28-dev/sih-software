# Slide 9: Out-of-Distribution (OOD) Guard & Software Safety

## 1. Out-of-Distribution (OOD) Guard Evaluation

### Evaluation Setup
Tested across $2,000$ real held-out in-domain test points and $1,998$ synthetic scenarios spanning modest, moderate, and severe extrapolations:

| Operational Regime | Sample Count | Mean Distance ($d_{\text{env}}$) | Interceptions ($d > 1.50$) | Action Taken |
|:-------------------|:-------------|:--------------------------------|:---------------------------|:-------------|
| **In-Domain Test Set** | $2,000$ | $0.031$ | **$0 / 2,000$ (0.0% FPR)** | Normal Serving |
| **Modest OOD** | $666$ | $0.442$ | $0 / 666$ | Permitted with inflated uncertainty |
| **Moderate OOD** | $666$ | $0.876$ | $16 / 666$ | Warned; routed to reference model |
| **Severe OOD (Storms)** | $666$ | $1.725$ | **$643 / 666$ (96.55% Recall)** | Emergency physics / fallback |

- **Primary Guard Metrics ($d_{\text{env}} = 1.50$)**:
  - $\text{TN} = 2,000, \text{FP} = 0, \text{TP} = 643, \text{FN} = 1,355$.
  - **False Positive Rate**: $\mathbf{0.0\%}$ | **Precision**: $\mathbf{100.0\%}$ | **Severe OOD Recall**: $\mathbf{96.55\%}$.
- **Warning Threshold ($d_{\text{env}} = 1.00$)**: Severe OOD Recall reaches $\mathbf{100.0\%}$.
- **Balanced Accuracy Explanation**: Overall balanced accuracy ($66.09\%$) reflects intentional design: modest/moderate shifts are allowed through with wider uncertainty rather than halting operations.

---

## 2. Software Safety & Failure Injection

| Defense Layer | Test Objective | Pass Rate | Audit Result |
|:--------------|:---------------|:----------|:-------------|
| **Adversarial Fuzzing** | 1,000 malformed inputs (NaN, Inf, negative speed, impossible draft) | **1,000 / 1,000 (100.0%)** | **PASS** |
| **Mandatory Edge Cases**| 16 boundary maritime operating conditions | **16 / 16 (100.0%)** | **PASS** |
| **Failure Injections**  | 10 runtime booster exceptions, corrupted configs, missing models | **10 / 10 (100.0%)** | **PASS** |

> **Scientific Boundary Statement**: "All evaluated invalid-input, edge-case, and injected-failure scenarios passed the defined software safety tests. We make no claim of an absolute 100% safe system in unmodeled environments."
