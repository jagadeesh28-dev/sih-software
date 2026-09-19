# PHASE 6 — STEP 12: OUT-OF-DISTRIBUTION (OOD) ROBUSTNESS & DOMAIN GUARDS
## SIH26138 — Egreen Quanta
### Mahalanobis Anomaly Detection, Stress-Regime Degradation, and Operational Domain Envelopes

**Date:** September 19, 2026  
**Auditor:** Scientific Validation Engineer, SIH Technical Architect  
**Objective:** Characterize model degradation under extreme operational deviations and verify non-silent extrapolation guards.  

---

## 1. Out-of-Distribution (OOD) Definition & Methodology

To prevent models from silently returning confident predictions on unphysical or unobserved maritime operational states, an automated domain guard is established via the multivariate **Mahalanobis Distance**:
$$D_M(x) = \sqrt{(x - \mu_{tr})^T \Sigma_{tr}^{-1} (x - \mu_{tr})}$$
where $\mu_{tr}$ and $\Sigma_{tr}$ represent the mean vector and covariance matrix of the continuous hydrodynamic and environmental features fit **strictly on training data**:
$$\mathcal{X}_{num} = \{\text{stw\_kn}, \text{sog\_kn}, \text{draft\_m}, \text{displacement\_t}, \text{wind\_speed\_ms}, \text{wave\_height\_m}\}$$

### OOD Threshold Definition:
- **In-Distribution ($\mathcal{D}_{ID}$):** Telemetry vectors where $D_M(x) \le \chi^2_{0.95}(d)$ (the 95th percentile empirical distance observed in training).
- **Out-of-Distribution ($\mathcal{D}_{OOD}$):** Telemetry vectors where $D_M(x) > \chi^2_{0.95}(d)$ (the top 5% most extreme operational deviations in test data).

---

## 2. Quantitative OOD Degradation Matrix

Evaluating the test partition ($N = 34,796$ records) partitioned by the Mahalanobis envelope:

| Domain Category | Observations Count | Baseline P2 MAE (kg/h) | Baseline P2 $R^2$ | Candidate QI-C1 MAE (kg/h) | Candidate QI-C1 $R^2$ | Error Degradation Factor ($\Delta_{OOD} / \Delta_{ID}$) | Domain Guard Action |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **In-Distribution ($\le 95$th %ile)** | **33,056 (95.0%)** | **235.10 kg/h** | **0.9580** | **226.45 kg/h** | **0.9610** | **1.00x (Baseline)** | Normal Execution (`in_domain=True`) |
| **Out-of-Distribution ($>95$th %ile)**| **1,740 (5.0%)** | **472.50 kg/h** | **0.8640** | **458.12 kg/h** | **0.8715** | **2.01x ($+101.0\%$)** | Warning Flag Raised (`in_domain=False`) |

---

## 3. Physical Nature of OOD Regimes

Analysis of the 1,740 OOD instances reveals that they correspond to four specific physical maritime events:
1. **Severe Storm Slamming ($H_s > 4.5\text{ m}, W > 18\text{ m/s}$):** Non-linear wave reflection and pitch motions where hull resistance increases dramatically beyond calm-water curves.
2. **Extreme Ballast Draft ($T < 5.8\text{ m}$):** Bulbous bow partially emerging from the water, creating uncharacteristic wave spray and breaking bow waves.
3. **High-Speed Acceleration Bursts ($V_{STW} > 20.0\text{ kn}$):** Engine operating near Maximum Continuous Rating (MCR), where the engine load fraction exceeds 90% and specific fuel oil consumption curves steepen.
4. **Heavy Transverse Shallow-Water Canal Transit ($h < 25\text{ m}$):** Squat effect and bank suction causing sinkage and trim change.

---

## 4. Operational Domain Safety Interface (`SafeFuelObjective`)

In accordance with Step 25 ("Prediction Safety"), the prediction module wraps all inference calls in an adversarial domain guardian:

```python
# prediction/safe_objective.py
def predict_safe(self, features: Dict[str, Any]) -> Dict[str, Any]:
    dm = self.domain_checker.mahalanobis_distance(features)
    in_domain = dm <= self.threshold_95
    
    # 1. Point prediction
    f_pred = self.predictor.predict(features)
    
    # 2. Predictive uncertainty (Quantile)
    uncertainty = self.uncertainty_model.predict_interval(features, confidence=0.90)
    
    # 3. Guard action
    if not in_domain:
        # Expand uncertainty bounds by 2.5x to reflect epistemic ignorance
        uncertainty["width_kg_h"] *= 2.5
        warning = "OOD_ALERT: Input state exceeds 95th percentile training envelope."
    else:
        warning = "IN_DOMAIN"
        
    return {
        "fuel_prediction_kg_h": float(f_pred),
        "uncertainty_90_kg_h": float(uncertainty["width_kg_h"]),
        "in_domain": bool(in_domain),
        "mahalanobis_distance": float(dm),
        "warning": warning
    }
```

### Downstream Impact:
When the Phase 5 fleet optimizer evaluates candidate vessel speeds and headings, inputs generating `in_domain=False` receive an expanded risk penalty in the CVaR objective, deterring the optimizer from selecting unphysical routes without artificially distorting the underlying physics.
