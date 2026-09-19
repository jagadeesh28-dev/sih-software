# System Architecture: Egreen Quanta (v1.0.0)

Egreen Quanta integrates naval architecture, machine learning, quantum-inspired evolutionary computing, and multi-objective optimization into an industrial-grade Decision Support System (DSS).

---

## 1. High-Level Architectural Pipeline

```
                         [ SENSOR TELEMETRY ]
                     (173,974 Validated Records)
                                  │
                                  ▼
                   [ FEATURE CONTRACT VALIDATOR ]
                     (PHASE7/config/feature_contract.yaml)
                                  │
                                  ▼
                    [ OPERATING DOMAIN GUARD ]
                     (prediction/domain_checker.py)
                                  │
                                  ▼
                   [ FIRST-PRINCIPLES PHYSICS ]
                     (Holtrop-Mennen + STAwave-2 + Wind)
                                  │
                 ┌────────────────┴────────────────┐
                 │                                 │
                 ▼                                 ▼
         [ MODEL-REAL-04 ]                      [ QI-C1 ]
       Classical 14-Feature ML             QIEA 8-Feature Selection
       Reference / Fallback                + LightGBM Residual (Primary)
                 │                                 │
                 └────────────────┬────────────────┘
                                  ▼
                   [ CONFORMAL UNCERTAINTY GATE ]
                    (models/conformal_quantiles.json)
                                  │
                                  ▼
                  [ MECHANICAL SHAFT ENERGY LAYER ]
                    (E_shaft = Integral P_B dt)
                                  │
                                  ▼
                  [ GREEN ALTERNATIVE FUEL SCENARIOS ]
                   (Bio-Methanol, Ammonia, LH2)
                                  │
                                  ▼
                  [ REGULATORY EMISSIONS ENGINE ]
                   (IMO CII / FuelEU / EU ETS)
                                  │
                                  ▼
                  [ PHASE 5 FLEET OPTIMIZER ]
                   (Deb Feasibility + Hungarian Repair)
                                  │
                                  ▼
                  [ OPERATOR DECISION SUPPORT ]
```

---

## 2. Core Architectural Subsystems

### 2.1 Feature Contract Gatekeeper
Enforces strict typing, units, missing-value imputation policies, and physical bounds across the 14 canonical inputs of `CONFIG_REAL_A`. Rejects any payload with NaN, Inf, or impossible naval parameters (e.g. $STW < 0$ or Displacement $< 500\text{ t}$).

### 2.2 First-Principles Physics Backbone (`physics/`)
Computes calm water resistance via Holtrop-Mennen (1982/1984), added wave resistance via IMO STAwave-2, and aerodynamic drag via Blendermann formulations. Speed calculations are strictly locked to Speed Through Water (STW) to respect hydrodynamic laws.

### 2.3 Dual-Engine Model Routing (`src/qi_prediction/serving.py`)
- **NORMAL State:** Evaluates `QI-C1` (8 features selected by QIEA) when operating states are well within the empirical domain envelope ($dist \le 1.00$).
- **FALLBACK State:** Seamlessly routes to frozen `MODEL-REAL-04` (14 features) if the query is near boundary ($1.00 < dist \le 1.50$) or if high uncertainty is detected.
- **EMERGENCY State:** Falls back to first-principles uncorrected physics if ML components fail.
- **REJECT State:** Safely halts inference if severe OOD ($dist > 3.00$) or physical violations occur.

### 2.4 Conformal Predictive Uncertainty Gate
Derived strictly from the validation partition, the system calculates symmetric non-conformity quantiles $q_{\alpha}$ guaranteeing that the interval $[\hat{y} - q_{\alpha}, \hat{y} + q_{\alpha}]$ captures true fuel consumption with nominal coverage (e.g., $90\%$). Extrapolation distance scales the interval dynamically to reflect epistemic risk.

### 2.5 Thermodynamic Alternative Fuel Layer
Applies the principle of invariant mechanical shaft work:
$$E_{shaft} = \int P_B(t) dt = m_{\text{fuel}} \times \text{LHV}_{\text{fuel}} \times \eta_{\text{thermal}}$$
Allows operators to evaluate green alternative bunker options (bio-methanol, green ammonia, liquid hydrogen) without fabricating non-existent telemetry.

### 2.6 Multi-Objective Green Fleet Optimizer (`optimization/`)
Optimizes fleet voyage speed schedules, cargo assignments, bunker selections, and shore power connections. Combines Deb's feasibility-first constraint handling with Hungarian bipartite matching repair to eliminate duplicate port calls and guarantee $100\%$ feasible sailing schedules.
