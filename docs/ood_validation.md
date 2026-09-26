# Out-of-Distribution (OOD) Guard & Envelope Validation Report
**System Component**: Production Domain Guard (`prediction/domain_checker.py` & `src/qi_prediction/serving.py`)  
**Evaluation Protocol**: Multi-Dimensional Empirical Envelope Distance  
**Audit Date**: September 2026  

---

## 0. Revalidation (2026-09-24) — CURRENT. Sections 1 onward are HISTORICAL.

### 0.1 Findings from the forensic analysis
1. **Distance.** For each feature *j*, $\delta_j = \max(0, x_j-\max_j, \min_j-x_j)\,/\,\max(\max_j-\min_j, \sigma_j)$, using training-split statistics (`models/domain_checker.json`). Any point inside the training box scores exactly 0.
2. **Normalisation.** Each exceedance is expressed in units of that feature's training span.
3. **Dilution (defect).** The previous score was $\sqrt{\sum_j\delta_j^2/n}$ over every feature present in the *sanitized* input. The serving contract imputes five missing environmental fields (wind/wave direction, wave period, current speed/direction). They count as in-range dimensions, which inflates *n* and lowers the score. For the storm demo, the score over the 7 supplied features is 1.789; with the 5 imputed zeros it becomes $1.789\sqrt{7/12}=1.366$.
4. **Dominant features.** For the storm: displacement 3.28 spans, draft 2.75, wave height 1.46, wind 1.18, STW 0.56, SOG 0.52, depth 0.
5. **Threshold origin.** The thresholds 1.00, 1.50 and 3.00 are production config defaults in units of training spans. Because every in-envelope point scores 0, they are not statistically fitted; they state how far beyond the observed range a value may lie.
6. **Evidence that depended on the old implementation:** `results/audit/detailed_ood_metrics.json`, `results/audit/safety_test_matrix.json`, claims C-05 and CQ-03, release gates G6 and G12, and demo scene 5.
7. **Demo scenes exercising OOD:** scene 5 (storm), plus scene 6 for routing under failure.
8. **Single-feature bypass (defect).** With RMS aggregation, a single extreme feature is diluted by the normal ones. Draft 22 m (2.75 spans beyond the envelope) with normal speed and displacement scored 0.79, which is IN DOMAIN.
9. **Evaluation/serving mismatch (defect).** The published 96.55% severe recall was scored on raw, non-imputed samples. Scored the way serving actually scores inputs, the severe recall of the deployed guard was **3.15%**. The storm's WARNING/FALLBACK result was therefore not the intended design: every storm-like generator sample was meant to be severe OOD.

### 0.2 Change (no threshold changed, no special cases)
- **Distance = L∞ over supplied features.** $d_{env}=\max_{j\in S}\delta_j$, where *S* is the set of features actually supplied; serving-contract defaults are excluded. This makes the score invariant to how many in-range measurements accompany an extreme one, and in-envelope points still score 0.
- **Unknown vessel type → REJECT** as categorical out-of-distribution. Previously it was scored with the `passenger_cruise` category, which was silent generic mapping.
- **`vessel_type` is a required input.** A missing type was previously defaulted to "ContainerShip" and then mapped as above; it is now an invalid-input rejection with a field-level message.
- **Warnings name the dominant feature** and its exceedance in spans.

### 0.3 Fresh results — FRESHLY COMPUTED (`results/audit/detailed_ood_metrics.json`, seed 42, serving path)
In-domain: 2,000 real test-split records. Synthetic sets: 666 each of modest, moderate and severe (same generator as before).

| Band (d_env >) | In-domain FPR | Modest | Moderate | Severe | Precision | Balanced acc. |
|---|---|---|---|---|---|---|
| 1.00 warning | 0.0% | 100% | 100% | 100% | 100% | 100.0% |
| 1.50 OOD | 0.0% | 0% (warning band) | 100% | 100% | 100% | 83.33% |
| 3.00 reject | 0.0% | 0% | 0% | 55.41% | 100% | 59.23% |

Distance ranges: modest 1.003–1.293, moderate 1.583–2.164, severe 2.369–3.832. The full 34,796-row test split also gives 0% at both the 1.00 and 1.50 bands.

Routing under the new guard:

| Case | Result |
|---|---|
| Normal Poseidon | NORMAL routing (WARNING only for the router's own high-uncertainty flag) |
| Modest excursion (draft 13.5 m, d = 1.10) | WARNING + MODEL-REAL-04 FALLBACK |
| Single extreme feature (draft 22 m, d = 2.75) | OOD, physics emergency estimate, LOW confidence |
| Storm demo (d = 3.28, dominant: displacement) | REJECT, no prediction |
| Unknown vessel type | REJECT (categorical OOD) |

### 0.4 Superseded reference — HISTORICAL, not current
The earlier figures (0.0% FPR; severe recall 96.55% at 1.50, 100% at 1.00; modest and moderate 0% at both) were produced by RMS aggregation on non-imputed samples. They are retained below for traceability only.

### 0.5 Remaining limitations
- The synthetic OOD populations are generator-defined, not observed storms. No real extreme-weather telemetry exists in the dataset.
- The envelope is an axis-aligned box. Joint combinations that are individually in range but never co-occurred are not detected; a density- or hull-based detector would be needed for that.
- `prediction/domain_checker.py`, used by the optimizer surrogates, has its own distance and was not changed.

---

## 1. OOD Detection Methodology & Mathematics
The OOD guard evaluates whether incoming operational telemetry falls within the empirical multidimensional convex hull of the training data.
For each continuous feature $j \in \{1, \dots, D\}$, let $[\min_j, \max_j]$ and $\sigma_j$ denote the empirical bounds and standard deviation observed on the **training split** ($104,384$ records).

For an incoming observation $\mathbf{x}$, the normalized boundary exceedance $\delta_j(\mathbf{x})$ is defined as:
$$\delta_j(\mathbf{x}) = \begin{cases} 
\frac{x_j - \max_j}{\max(\max_j - \min_j, \sigma_j)} & \text{if } x_j > \max_j \\
\frac{\min_j - x_j}{\max(\max_j - \min_j, \sigma_j)} & \text{if } x_j < \min_j \\
0 & \text{if } \min_j \le x_j \le \max_j 
\end{cases}$$

The total **Normalized Envelope Distance** $d_{\text{env}}(\mathbf{x})$ is the root-mean-square boundary deviation across all $D$ features:
$$d_{\text{env}}(\mathbf{x}) = \sqrt{\frac{1}{D} \sum_{j=1}^D \delta_j(\mathbf{x})^2}$$

### Decision Thresholds (Calibrated Strictly on Training Data)
- **$d_{\text{env}} \le 1.00$**: **Core In-Domain (NORMAL)** $\to$ QI-C1 evaluated with high confidence.
- **$1.00 < d_{\text{env}} \le 1.50$**: **Near-Boundary Warning (FALLBACK)** $\to$ Routed to reference MODEL-REAL-04 with medium confidence.
- **$1.50 < d_{\text{env}} \le 3.00$**: **Out-of-Distribution (EMERGENCY)** $\to$ ML models disabled; unadjusted physics estimate served with low confidence.
- **$d_{\text{env}} > 3.00$**: **Severe OOD Violation (REJECT)** $\to$ Request hard rejected.

> **Zero Test Leakage**: Thresholds ($1.00, 1.50, 3.00$) were calibrated exclusively on training split envelopes. Zero threshold tuning was performed on the test split.

---

## 2. Experimental Population Setup

### In-Domain Population
- **Sample Size**: $2,000$ points drawn uniformly at random from the held-out forward temporal test split ($34,796$ rows).
- **Provenance**: Real vessel sea trials under nominal operational conditions.

### Synthetic OOD Populations
To rigorously evaluate detection recall across operational severity levels without corrupting real telemetry, three distinct synthetic populations ($666$ samples each, total $1,998$) were constructed:
1. **Modest OOD (Mild Extrapolation)**: Speed $20.5 - 23.0\text{ kn}$, draught $13.0 - 14.5\text{ m}$, waves $3.5 - 5.0\text{ m}$.
2. **Moderate OOD (Elevated Environmental Forcing)**: Speed $25.0 - 29.0\text{ kn}$, draught $16.0 - 19.0\text{ m}$, waves $7.0 - 10.0\text{ m}$, winds $25 - 35\text{ m/s}$.
3. **Severe OOD (Extreme Sea State / Storm)**: Speed $32.0 - 35.0\text{ kn}$, draught $20.0 - 24.0\text{ m}$, waves $12.0 - 16.0\text{ m}$, winds $42 - 55\text{ m/s}$.

---

## 3. Confusion Matrix & Quantitative Evaluation

### Primary OOD Guard Evaluation ($d_{\text{env}} > 1.50$)

| Evaluation Metric | Mathematical Definition | Empirical Value | Audit Assessment |
|:------------------|:------------------------|:----------------|:-----------------|
| **True Negatives (TN)** | Real In-Domain correctly accepted | $\mathbf{2,000 / 2,000}$ | Perfect in-domain preservation |
| **False Positives (FP)** | Real In-Domain falsely flagged OOD | $\mathbf{0 / 2,000}$ | **$0.0\%$ False Positive Rate** |
| **True Positives (TP)** | OOD scenarios correctly flagged | $\mathbf{643 / 1,998}$ | Concentrated on Severe OOD |
| **False Negatives (FN)** | OOD scenarios passing threshold | $\mathbf{1,355 / 1,998}$ | Modest/Moderate extrapolations |
| **Precision** | $\frac{\text{TP}}{\text{TP} + \text{FP}}$ | $\mathbf{100.0\%}$ | Zero false alarms |
| **Recall (Severe OOD)** | $\frac{\text{TP}_{\text{severe}}}{\text{Severe Count}}$ | $\mathbf{96.55\%}$ | $643 / 666$ severe storms intercepted |
| **Specificity** | $\frac{\text{TN}}{\text{TN} + \text{FP}}$ | $\mathbf{100.0\%}$ | Maximum operational availability |
| **False Positive Rate (FPR)** | $\frac{\text{FP}}{\text{TN} + \text{FP}}$ | $\mathbf{0.0\%}$ | Verified non-disruptive to normal operations |
| **Balanced Accuracy** | $\frac{\text{Recall} + \text{Specificity}}{2}$ | $\mathbf{66.09\%}$ | Global across all modest-to-severe tiers |

---

## 4. Disaggregated Performance by OOD Severity

| OOD Category | Sample Count | Mean Distance ($d_{\text{env}}$) | Distance Range | Detection Count ($d > 1.50$) | Recall ($d > 1.50$) | System Response |
|:-------------|:-------------|:--------------------------------|:---------------|:-----------------------------|:--------------------|:----------------|
| **In-Domain Test** | 2,000 | $0.031$ | $[0.000, 0.421]$ | $0 / 2,000$ | $0.0\%$ (FPR) | Normal QI-C1 serving |
| **Modest OOD** | 666 | $0.442$ | $[0.384, 0.503]$ | $0 / 666$ | $0.0\%$ | Allowed through; conformal interval scaled by $+22\%$ |
| **Moderate OOD** | 666 | $0.876$ | $[0.714, 1.030]$ | $16 / 666$ | $2.4\%$ | Warned at $d>1.0$; routed to MODEL-REAL-04 fallback |
| **Severe OOD** | 666 | $1.725$ | $[1.390, 2.024]$ | $643 / 666$ | **$96.55\%$** | Hard fallback or Emergency Physics |

### Scientific Conclusion
The OOD Guard exhibits a smooth, graduated safety posture:
1. Mild operational variations are **not blocked**, preventing nuisance false alarms that cause operator fatigue. Instead, conformal uncertainty intervals are dynamically expanded.
2. Moderate variations activate the near-boundary warning gate, falling back from QI-C1 to the 14-feature reference baseline `MODEL-REAL-04`.
3. Extreme storm states and unphysical vessel speeds are intercepted with **$96.55\%$ recall**, safely routing the vessel to first-principles emergency physics.
