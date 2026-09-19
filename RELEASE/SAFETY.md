# Safety-Critical Engineering & Defensive Architecture
### SIH26138 — Egreen Quanta (v1.0.0)

Egreen Quanta is engineered according to safety-critical software principles to prevent ungrounded predictions, dangerous vessel dispatch recommendations, and silent extrapolation.

---

## 1. Defensive Layering Overview

```
[ UNVALIDATED OPERATIONAL SENSOR TELEMETRY ]
                     │
                     ▼
  [ LAYER 1: IMMUTABLE FEATURE CONTRACT ]
  - Enforces type, unit, and range constraints
  - Intercepts and rejects NaN, Inf, and impossible physics
  - 100% safe rejection across 1,000 automated stress tests
                     │
                     ▼
  [ LAYER 2: MULTI-DIMENSIONAL DOMAIN GUARD ]
  - Evaluates normalized Mahalanobis envelope distance
  - Distance > 1.00: Enters NEAR_BOUNDARY (routes to fallback)
  - Distance > 3.00: Enters SEVERE_OOD (halts and rejects)
                     │
                     ▼
  [ LAYER 3: DUAL-ENGINE SAFE ROUTING ]
  - Normal: Primary QI-C1
  - Fallback: MODEL-REAL-04 on boundary or high uncertainty
  - Emergency: PhysicsFuelPredictor if ML models fail
                     │
                     ▼
  [ LAYER 4: CONFORMAL UNCERTAINTY MONITOR ]
  - Calibrated 80%, 90%, 95% predictive intervals
  - Flags operational warnings if interval width > 1200 kg/h
                     │
                     ▼
  [ LAYER 5: OPTIMIZER SAFE FUEL OBJECTIVE ]
  - Injects heavy mathematical penalty ($10,000 kg/h) for OOD
  - Deb's feasibility-first constraint handling
  - Prevents optimizer from exploiting model blind spots
```

---

## 2. Automated Stress Testing Summary

Across 1,000 automated stress tests (`PHASE7/results/prediction_stress_tests.csv`):
- **Corrupted Inputs:** 150 tests with NaN, Inf, negative speeds, and string types $\to$ **100% Safely Rejected**.
- **Missing Inputs:** 150 tests with missing mandatory columns $\to$ **100% Safely Rejected**.
- **Extreme Extrapolations:** 100 tests with speed $>35\text{ kn}$ or draft $>25\text{ m}$ $\to$ **100% Safely Rejected**.
- **Physical Inconsistencies:** 100 tests with speed $20\text{ kn}$ but zero displacement $\to$ **100% Safely Rejected**.
- **Deterministic Repeatability:** 100 duplicate tests verified zero prediction variance ($\text{std} = 0.000$).

---

## 3. Failure Injection Protocol (F1–F10)

The system underwent deliberate fault injection across ten distinct failure modes (`PHASE7/results/failure_injection.csv`):
- **F1 (Missing Telemetry):** Safely rejected at schema layer.
- **F2 (Corrupted Telemetry):** Safely rejected with informative warning.
- **F3 (QI-C1 Booster Unloaded):** Seamless fallback to `MODEL-REAL-04`.
- **F4 (QI-C1 Inference Exception):** Trapped in try-except block; routed to `MODEL-REAL-04`.
- **F5 (OOD Extrapolation State):** Trapped by envelope guard; routed to fallback or rejected.
- **F6 (All ML Models Crash):** Trapped; routed to emergency theoretical physics.
- **F7 (Malformed Request Type):** Safely rejected with `TypeError`.
- **F8 (Negative Speed Input):** Intercepted by physical sanity checker.
- **F9 (Missing Configuration File):** Fallback to built-in default constants.
- **F10 (Missing Model Booster File):** Dynamic fallback to reference physics.
