# Uncertainty Quantification & Conformal Calibration Report
**System**: Egreen Quanta Predictive Engine  
**Methodology**: Inductive Conformal Prediction (Non-Conformity Measure: Absolute Residual $|y - \hat{y}|$)  
**Calibration Set**: 34,794 forward temporal validation records (zero test leakage)  
**Evaluation Set**: 34,796 held-out forward temporal test records  
**Audit Date**: September 2026  

---

## 1. Mathematical Formulation
Conformal prediction guarantees finite-sample marginal coverage without distributional assumptions.
Given a calibration set $\mathcal{D}_{\text{val}} = \{(\mathbf{x}_i, y_i)\}_{i=1}^{n_{\text{val}}}$, we compute non-conformity scores:
$$s_i = |y_i - \hat{y}_i|$$
For a desired nominal coverage level $1 - \alpha$ (e.g., $90\%$ or $95\%$), the calibrated conformal quantile $\hat{q}_{1-\alpha}$ is defined as:
$$\hat{q}_{1-\alpha} = \text{Quantile}\left(s_1, \dots, s_{n_{\text{val}}}; \frac{\lceil (n_{\text{val}} + 1)(1 - \alpha) \rceil}{n_{\text{val}}}\right)$$
The prediction interval for a new test point $\mathbf{x}_{\text{test}}$ is:
$$\mathcal{C}_{1-\alpha}(\mathbf{x}_{\text{test}}) = \left[ \max(0, \hat{y}(\mathbf{x}_{\text{test}}) - \hat{q}_{1-\alpha}), \;\; \hat{y}(\mathbf{x}_{\text{test}}) + \hat{q}_{1-\alpha} \right]$$

---

## 2. Overall Coverage vs. Sharpness Comparison

Both models were evaluated on the exact same $34,796$ test records under nominal $90\%$ ($\alpha = 0.10$) and $95\%$ ($\alpha = 0.05$) levels.

| Metric | Nominal 90% Level | Nominal 90% Level | Nominal 95% Level | Nominal 95% Level |
|:-------|:-----------------:|:-----------------:|:-----------------:|:-----------------:|
| **Model** | **MODEL-REAL-04** | **QI-C1** | **MODEL-REAL-04** | **QI-C1** |
| **Calibrated Conformal Quantile ($\hat{q}$)** | $1,136.85\text{ kg/h}$ | **$782.47\text{ kg/h}$** | $1,444.43\text{ kg/h}$ | **$1,384.47\text{ kg/h}$** |
| **Prediction Interval Coverage (PICP)** | $95.05\%$ | **$93.56\%$** | $97.29\%$ | **$96.49\%$** |
| **Mean Pred. Interval Width (MPIW)** | $2,273.70\text{ kg/h}$ | **$1,564.93\text{ kg/h}$** | $2,888.85\text{ kg/h}$ | **$2,768.94\text{ kg/h}$** |
| **Median Interval Width** | $2,273.70\text{ kg/h}$ | **$1,564.93\text{ kg/h}$** | $2,888.85\text{ kg/h}$ | **$2,768.94\text{ kg/h}$** |
| **Normalized Width (by Fuel Span)** | $0.3166$ | **$0.2179$** | $0.4022$ | **$0.3855$** |
| **Normalized Width (by Fuel Std Dev)** | $1.1459$ | **$0.7887$** | $1.4559$ | **$1.3955$** |
| **Coverage Error ($\text{PICP} - \text{Nominal}$)** | $+5.05\%$ | **$+3.56\%$** | $+2.29\%$ | **$+1.49\%$** |
| **Interval Width / Mean Fuel ($2,444.2\text{ kg/h}$)** | $0.9302$ | **$0.6402$** | $1.1819$ | **$1.1328$** |
| **Sharpness Advantage ($\Delta\text{MPIW}$)** | Baseline | **+31.17% Sharper** | Baseline | **+4.15% Sharper** |

---

## 3. The Coverage-Width Tradeoff Analysis
A critical scientific principle enforced in this release is that **higher coverage is not automatically better**. 
- A trivial predictor outputting $[0, \infty)$ attains $100\%$ coverage but provides zero decision-support value.
- `MODEL-REAL-04` attains $95.05\%$ coverage at a nominal $90\%$ setting, but does so with an inflated interval width of $2,273.70\text{ kg/h}$.
- `QI-C1` satisfies the nominal $90\%$ reliability guarantee with $93.56\%$ coverage, while reducing interval width by **$708.77\text{ kg/h}$ ($31.17\%$ sharper)**.
- Therefore, `QI-C1` delivers a superior coverage-width Pareto efficiency for ship operators.

---

## 4. Calibration Disaggregation by Vessel

### Nominal 90% Coverage Level

| Vessel Identifier | Vessel Class | Test Records | MODEL-REAL-04 PICP | QI-C1 PICP | MPIW Difference | Mean Vessel Fuel Rate |
|:------------------|:-------------|:-------------|:-------------------|:-----------|:----------------|:----------------------|
| **CPS_Poseidon** | Cruise Passenger | 21,085 | $91.83\%$ | $89.69\%$ | QI-C1 is $708.8\text{ kg/h}$ sharper | $3,551.20\text{ kg/h}$ |
| **CPS_Triton** | Small Ferry | 5,070 | $100.00\%$ | $100.00\%$ | QI-C1 is $708.8\text{ kg/h}$ sharper | $609.84\text{ kg/h}$ |
| **OSS_Ceto** | Offshore Supply | 8,641 | $100.00\%$ | $99.21\%$ | QI-C1 is $708.8\text{ kg/h}$ sharper | $819.70\text{ kg/h}$ |

*Finding*: Coverage is conservative ($99.2\% - 100.0\%$) on smaller vessels (Triton and Ceto) because their variance is lower than the fleet-wide calibration quantile.

---

## 5. Calibration Disaggregation by Operating Regime

### Nominal 90% Coverage Level

| Operating Regime | Speed Range | Test Records | MODEL-REAL-04 PICP | QI-C1 PICP | Regime Mean Fuel Rate |
|:-----------------|:------------|:-------------|:-------------------|:-----------|:----------------------|
| **Low Speed / Manoeuvring** | $\text{STW} \le 12.0\text{ kn}$ | 17,439 | $98.96\%$ | $98.27\%$ | $1,057.50\text{ kg/h}$ |
| **Standard Cruise** | $12.0 < \text{STW} \le 16.0\text{ kn}$ | 6,050 | $99.60\%$ | $97.93\%$ | $1,551.06\text{ kg/h}$ |
| **High Speed / Recovery** | $\text{STW} > 16.0\text{ kn}$ | 11,307 | $86.57\%$ | $83.95\%$ | $5,061.15\text{ kg/h}$ |

*Operational Recommendation*: At high speeds ($>16\text{ kn}$), fuel consumption variance increases non-linearly. The system dynamically flags high-speed predictions with an uncertainty elevation warning and applies extrapolation penalty scaling when operating near envelope edges.
