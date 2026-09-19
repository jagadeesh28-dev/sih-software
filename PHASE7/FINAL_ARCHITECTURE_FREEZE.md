# FINAL ARCHITECTURE FREEZE: EGREEN QUANTA
## SIH26138 — Egreen Quanta
### Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization

**RELEASE VERSION:** `v1.0.0`  
**RELEASE DATE:** September 19, 2026  
**SYSTEM STATUS:** **FROZEN & IMMUTABLE**  
**GIT COMMIT:** `20309b214b9540a7363b7365e442a222cd9c49a1`  

---

## 1. Frozen System Architecture Specification

The final production architecture for SIH26138 (Egreen Quanta) is officially frozen across all eleven core subsystems:

```
                                [ REAL SENSOR TELEMETRY ]
                                (173,974 Active Records)
                                           │
                                           ▼
                             [ FEATURE CONTRACT GATEKEEPER ]
                                (PHASE7/config/feature_contract.yaml)
                                           │
                                           ▼
                                [ DOMAIN ENVELOPE GUARD ]
                                 (prediction/domain_checker.py)
                                           │
                                           ▼
                            [ FIRST-PRINCIPLES PHYSICS BACKBONE ]
                             (Holtrop-Mennen + STAwave-2 + Wind Drag)
                                           │
                       ┌───────────────────┴───────────────────┐
                       │                                       │
                       ▼                                       ▼
               [ MODEL-REAL-04 ]                            [ QI-C1 ]
            LightGBM 14-Feature ML                   QIEA 8-Feature Selection
            Reference / Fallback Engine              Primary Prediction Engine
                       │                                       │
                       └───────────────────┬───────────────────┘
                                           ▼
                             [ CONFORMAL UNCERTAINTY GATE ]
                              (models/conformal_quantiles.json)
                                           │
                                           ▼
                           [ MECHANICAL SHAFT ENERGY CONVERSION ]
                             (E_shaft = Integral P_B(t) dt)
                                           │
                                           ▼
                        [ ALTERNATIVE FUEL THERMODYNAMIC LAYER ]
                          (VLSFO, Bio-Methanol, Ammonia, LH2)
                                           │
                                           ▼
                          [ REGULATORY GHG ACCOUNTING ENGINE ]
                         (IMO CII / FuelEU Maritime / EU ETS)
                                           │
                                           ▼
                           [ PHASE 5 MULTI-OBJECTIVE OPTIMIZER ]
                           (Hybrid A5: Deb Feasibility + Hungarian)
                                           │
                                           ▼
                         [ HUMAN-IN-THE-LOOP DECISION SUPPORT ]
```

---

## 2. Frozen Subsystem Ledger

| Subsystem Component | Exact Implementation File | Version / Checksum | Operational Role |
| :--- | :--- | :--- | :--- |
| **Feature Contract** | `PHASE7/config/feature_contract.yaml` | `v1.0.0-frozen` | Immutable 14-feature schema, unit, and range contract. |
| **Physics Backbone** | `prediction/physics_predictor.py` | `v1.0.0-first-principles` | Theoretical naval architecture resistance baseline. |
| **Domain Guard** | `prediction/domain_checker.py` | `models/domain_checker.json` | Mahalanobis & bounding-box OOD detector. |
| **Primary Predictor** | `src/qi_prediction/serving.py` | `models/qi_c1.txt` | QIEA-selected 8-feature LightGBM residual model. |
| **Reference Fallback** | `src/qi_prediction/serving.py` | `models/model_real_04.txt` | Classical 14-feature LightGBM residual model. |
| **Uncertainty Gate** | `src/qi_prediction/serving.py` | `models/conformal_quantiles.json` | Conformal prediction intervals (80%, 90%, 95%). |
| **Safe Fuel Objective**| `prediction/safe_objective.py` | `v1.0.0-frozen` | Optimization interface with defensive OOD penalties. |
| **Alternative Fuels** | `configs/fuels.yaml` | `v1.0.0-frozen` | Invariant mechanical shaft energy conversion layer. |
| **Regulatory Engine** | `optimization/regulatory.py` | `configs/regulations.yaml` | Separate TtW, WtT, and WtW compliance accounting. |
| **Fleet Optimizer** | `optimization/fleet_evaluator_phase4.py` | `v1.0.0-frozen` | Multi-objective fleet routing, speed, and bunkering. |
| **Decision Support** | `src/visualization/plots.py` | `v1.0.0-frozen` | Human-in-the-loop Pareto frontier visualization. |

---

## 3. Immutability Mandate

Under the SIH 2026 engineering release freeze:
1. No further algorithmic changes or objective function modifications are permitted.
2. The benchmark evaluation budgets, datasets, and random seeds are permanently locked.
3. All production serving requests must pass through the `ProductionFuelPredictor` interface.

**SYSTEM OFFICIALLY FROZEN AT RELEASE v1.0.0.**
