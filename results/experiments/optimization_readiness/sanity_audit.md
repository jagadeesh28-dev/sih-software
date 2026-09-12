# Physical Sanity & Monotonicity Audit
**Document ID:** `AUDIT-SANITY-001`  
**Software Version:** 0.2.1 | **Git Commit:** `febed1ae38a3b2be34235dc6436b5fc7d493808b`  

---

## 1. Audit Summary Matrix

| Check ID | Check Name | Status | Violations | Classification | Details |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `SANITY-01` | **Negative Fuel Flow Check** | `PASS` | 0 | `ACCEPTABLE_NON-MONOTONICITY` | Zero negative predictions observed across entire operational envelope. |
| `SANITY-02` | **Near-Zero Fuel at High Power** | `PASS` | 0 | `ACCEPTABLE_NON-MONOTONICITY` | Model maintains physically consistent high fuel rates under high shaft power. |
| `SANITY-03` | **Shaft Power Monotonicity** | `PASS` | 0 | `ACCEPTABLE_NON-MONOTONICITY` | Observed 0 local inversions exceeding 5 kg/h threshold. |
| `SANITY-04` | **Speed Monotonicity (Coupled Hydrodynamics)** | `PASS` | 0 | `ACCEPTABLE_NON-MONOTONICITY` | Observed 0 inversions across speed range. |
| `SANITY-05` | **Decision Tree Step Discontinuity Audit** | `PASS` | 0 | `POSSIBLE_MODEL_ARTIFACT` | Max discrete jump between adjacent 500 kW steps was 44.41 kg/h (typical tree artifact). |
| `SANITY-06` | **Extrapolation Trough Protection** | `PASS` | 0 | `EXTRAPOLATION_REGION` | Extreme power was flagged as OUT_OF_DOMAIN with penalized objective 18805.2 kg/h. |

---

## 2. Scientific Interpretation
1. **Physical Expectation Adherence**: Zero negative fuel predictions; fuel scales realistically with power.
2. **Model Artifacts (Decision Tree Steps)**: LightGBM piecewise constant jumps are normal surrogate behavior.
3. **Extrapolation Protection**: Ungrounded operating regions are flagged by DomainChecker and penalized by SafeFuelObjective.
