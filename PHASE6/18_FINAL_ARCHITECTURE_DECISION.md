# PHASE 6 — STEP 18: FINAL ARCHITECTURAL DECISION
## SIH26138 — Egreen Quanta
### Selection and Formal Justification of the Production Fleet Prediction Engine

**Date:** September 19, 2026  
**Decision Authority:** Lead Research Engineer, Technical Architect, Scientific Validation Panel  
**Selected Architectural Decision:** **OPTION B — CLASSICAL BASELINE + QI-C1 (DUAL-ENGINE ARCHITECTURE)**  

---

## 1. Architectural Options Considered

| Option ID | Architectural Configuration | Empirical Scientific Evidence | Architectural Decision |
| :--- | :--- | :--- | :--- |
| **Option A** | Pure Classical Physics + ML Residual Only | Stable, well-validated ($R^2 = 0.9501$), but lacks the $+44.7\%$ feature search diversity and sharper prediction intervals provided by QIEA. | Rejected (Suboptimal Exploration) |
| **OPTION B** | **Classical Baseline (`MODEL-REAL-04`) + Candidate `QI-C1` (QIEA/QPSO)** | **QI-C1 achieves competitive accuracy ($\text{MAE} = 237.96\text{ kg/h}$), superior search diversity ($H=0.2814$), and sharper conformal intervals ($598.40\text{ kg/h}$). Baseline P2 serves as an immutable fallback.** | **APPROVED & ADOPTED (Production Standard)** |
| **Option C** | Classical Baseline + Candidate `QI-C2` (MPS) | MPS tensor network suffered gradient divergence across 20 of 30 seeds ($\text{MAE} > 10^{11}\text{ kg/h}$). | **REJECTED (Severe Instability)** |
| **Option D** | Classical Baseline + `QI-C1` + `QI-C2` | Incorporating MPS degrades system reliability without providing compensating utility. | **REJECTED (Compromised Safety)** |
| **Option E** | Total Rejection of QI; Retain Classical Predictor Only | Ignores the experimentally proven diversity preservation of QIEA and sharper risk bounds. | Rejected (Overly Conservative) |

---

## 2. Production Dual-Engine Architecture Specification

To ensure both maximum innovation and uncompromised industrial safety, the Egreen Quanta platform adopts a **Dual-Engine Production Architecture**:

```
                              [Input Telemetry Stream]
                                         │
                                         ▼
                             [Physics Hydrodynamic Model]
                             (Holtrop-Mennen STW Pipeline)
                                         │
                     ┌───────────────────┴───────────────────┐
                     ▼                                       ▼
        [PRIMARY PREDICTION ENGINE]              [BENCHMARK & FALLBACK ENGINE]
            Candidate QI-C1                          Classical Baseline P2
        (QIEA-FS + QPSO-Tuned LightGBM)                 (MODEL-REAL-04)
                     │                                       │
        MAE: 237.96 kg/h, R2: 0.9530             MAE: 246.97 kg/h, R2: 0.9501
        High-Diversity Feature Subset            Frozen Reference Anchor
        Sharper 90% Bound (598.4 kg/h)           Ultra-Fast, Zero-Stochasticity
                     │                                       │
                     └───────────────────┬───────────────────┘
                                         ▼
                          [Operational Domain Guardian]
                                (SafeFuelObjective)
                            - Mahalanobis OOD Detector
                            - Conformal Quantile Risk Sizing
                            - Physical Bounds Enforcement
                                         │
                                         ▼
                         [Frozen Phase 5 Fleet Optimizer]
                            - Hungarian Route Allocation
                            - Deb's Constraint Handling
                            - Multi-Objective Pareto Dispatch
```

---

## 3. Industrial Safety & Fail-Safe Protocols

1. **Primary Operational Engine:** `QI-C1 (QIEA-FS + LightGBM Residual)` drives the real-time shipboard digital twin, voyages simulation, and fleet dispatch optimizer, utilizing its sharper predictive intervals to minimize unnecessary safety margins.
2. **Deterministic Fallback:** If telemetry inputs enter extreme OOD regimes or if QIEA feature masks encounter missing sensor streams, the system instantaneously and deterministically switches to `MODEL-REAL-04 (P2)`.
3. **Emergency Physical Floor:** If all data-driven modules experience telemetry dropout, the pure first-principles Holtrop-Mennen engine (`MODEL-REAL-01`) maintains vessel propulsion and fuel estimation without crashing the fleet scheduling layer.
