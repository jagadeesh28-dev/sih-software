# EGREEN QUANTA — DECISION TRACEABILITY & REPRODUCIBILITY AUDIT
**SIH26138 — Quantum-Inspired Fuel Consumption Prediction and Green Fleet Optimization**
**Verification Level: Production Hardening & Operational Audit**
**Date: September 2026**

---

## 1. Executive Summary & Zero-Mock Guarantee

This document provides complete, unbroken mathematical and architectural traceability for all decisions produced by **EGREEN QUANTA**. 

### The Zero-Mock Policy
- **Zero Synthetic KPIs**: Every key performance indicator (fuel burn rate, voyage cost, lifecycle GHG, conformal prediction interval, envelope distance) originates from executable backend physics and ML surrogates.
- **Zero Client-Side Fabrication**: The Next.js frontend console contains no `Math.random()`, no hardcoded simulation fixtures on operational screens, and no artificial "AI optimization" animations that do not mirror real background execution.
- **Auditable Input-to-Decision Pipeline**: Every dispatch advisory recommendation traces deterministically from raw environmental/hull inputs through hydrodynamic scaling, machine learning residual estimation, multi-objective Pareto optimization, and operator approval.

---

## 2. End-to-End Decision Pipeline Architecture

```
[1. REAL INPUT]
   Vessel Type, STW, SOG, Draft, Displacement, Environmental Weather, Fuel Type
       ↓
[2. DATA VALIDATION & SERVING CONTRACT]
   `prediction.feature_contract.validate_serving_point()`
   Checks physical bounds (Froude < 0.45, STW ∈ [5, 25], Draft ∈ [2, 16]m)
       ↓
[3. BASELINE HYDRODYNAMICS & ML RESIDUAL]
   `prediction.physics_predictor.PhysicsPredictor` (Holtrop-Mennen naval resistance)
   + `prediction.qi_predictor.QIC1VesselTypePredictor` (LightGBM residual booster)
       ↓
[4. FINITE-SAMPLE CONFORMAL UNCERTAINTY]
   `prediction.conformal_uncertainty.ConformalUncertainty`
   Calculates exact finite-sample conformal prediction interval: [y_lower, y_upper] at 1 - α coverage
       ↓
[5. CONVEX ENVELOPE OUT-OF-DOMAIN (OOD) GUARD]
   `prediction.domain_checker.DomainChecker`
   Computes convex envelope distance d_env against sea-trial hull dimensions
       ↓
[6. ADAPTIVE MODEL ROUTER & SAFETY FALLBACK]
   `prediction.router.ModelRouter`
   If d_env > 1.5 or surrogate failure → Divert to Reference Anchor `MODEL-REAL-04`
       ↓
[7. MULTI-LEG VOYAGE SCENARIO ENGINE]
   `src.evaluator.sih_engine.SIHEngine`
   Evaluates voyage itineraries, speed scheduling, route resistance, and port berth stays
       ↓
[8. MARITIME OPEX COST ENGINE]
   `src.evaluator.sih_engine.hourly_economics()`
   Bunker fuel consumption + Port shore-power tariffs + EU ETS / Carbon allowances
       ↓
[9. IMO LIFECYCLE GHG ACCOUNTING (MEPC.391(81))]
   `emissions.lifecycle_ghg.LifecycleGHGCalculator`
   Well-to-Tank (upstream fuel supply) + Tank-to-Wake (combustion) + Methane slip
       ↓
[10. QUANTUM-INSPIRED MULTI-OBJECTIVE OPTIMIZATION]
   `src.optimizers.hybrid_qi_a5.HybridQIA5` (QIEA + QPSO on Classical Hardware)
   Deb's parameter-free feasibility rule enforces zero deadline and cargo capacity breaches
       ↓
[11. PARETO NON-DOMINATED FRONTIER]
   `pareto.pareto_frontier.ParetoFrontier`
   Extracts non-dominated fleet dispatch plans balancing OPEX vs. WtW GHG vs. Delay
       ↓
[12. HUMAN-IN-THE-LOOP ADVISORY DECISION]
   `api.main.decide()`
   Operator reviews trade-offs and explicitly accepts/rejects dispatch before execution
       ↓
[13. IMMUTABLE AUDIT LEDGER]
   `api.main.audit_events()`
   Records complete dispatch vector, timestamps, operator remarks, and environmental inputs to SQLite
```

---

## 3. Metric-by-Metric Backend Traceability Matrix

Every operational metric visible on the EGREEN QUANTA Marine HMI is cross-referenced below to its exact source file, function, and scientific basis:

| Displayed Metric | UI Location | Unit | Source Code Reference | Scientific Formulation / Standard |
| :--- | :--- | :--- | :--- | :--- |
| **Predicted Fuel Consumption** | `Step 03 — Fuel Prediction` | `kg/h` | `prediction.hybrid_predictor.predict()` | $P_{brake} = \frac{R_{total} \cdot V}{\eta_D} + \text{Booster Residual}$; $\dot{m}_{fuel} = P_{brake} \cdot \text{SFOC}$ |
| **Conformal Prediction Interval** | `Step 03 — Fuel Prediction` | `kg/h` | `prediction.conformal_uncertainty.ConformalUncertainty` | Split conformal quantile non-conformity score: $\hat{y} \pm \hat{q}_{1-\alpha}(|y_i - \hat{y}_i|)$ |
| **Envelope Distance ($d_{env}$)** | `Step 03 — Prediction Drawer` | Unitless | `prediction.domain_checker.DomainChecker` | Normalized distance to minimum bounding hyper-rectangle of training sea-trials |
| **Fleet Total Fuel Burn** | `Step 04 — Fleet Optimizer` | `tonnes` | `src.evaluator.common_evaluator.evaluate()` | $\sum_{v \in \text{Fleet}} \int_0^{T_v} \dot{m}_{v}(t) \, dt$ across assigned demand voyage legs |
| **Total Voyage OPEX** | `Step 04 & 05 — Optimizer / Pareto` | `USD` | `src.evaluator.sih_engine.hourly_economics()` | $C_{total} = \sum (M_{fuel} \cdot P_{fuel} + E_{shore} \cdot T_{shore} + \text{GHG} \cdot P_{carbon})$ |
| **Well-to-Wake Lifecycle GHG** | `Step 04 & 05 — Optimizer / Pareto` | `tCO2e` | `emissions.lifecycle_ghg.LifecycleGHGCalculator` | $E_{WtW} = \sum (M_{fuel} \cdot (f_{WtT} + f_{TtW}) + M_{CH_4,slip} \cdot GWP_{20/100})$ |
| **Fleet Schedule Delay** | `Step 04 & 05 — Optimizer / Pareto` | `hours` | `src.evaluator.sih_engine.SIHEngine` | $\Delta T = \max(0, T_{arrival} - T_{deadline})$; hard penalization if $\Delta T > 0$ |
| **Cold Ironing Shore Power** | `Step 07 — Alternative Fuels` | `USD / tCO2e`| `tests.test_shore_power` | Port berth electrical connection substituting auxiliary diesel generators |
| **Pareto Dominance Classification**| `Step 05 — Decision Space` | Categorical | `pareto.pareto_frontier.ParetoFrontier` | Vector domination: $x \prec y \iff \forall i (f_i(x) \le f_i(y)) \land \exists j (f_j(x) < f_j(y))$ |
| **Deb Feasibility Status** | `Step 04 — Optimizer Card` | Categorical | `src.optimizers.deb_rule.DebRule` | Feasible solutions strictly dominate all infeasible candidates regardless of fitness |

---

## 4. Decision Record Export Schema

Every decision approved by an operator can be exported as a certified Decision Record (both JSON and CSV format). The structured JSON schema captures complete environmental and algorithmic provenance:

```json
{
  "export_type": "EGREEN_QUANTA_DECISION_RECORD",
  "generated_at": "2026-09-26T22:45:00.000Z",
  "job_id": "OPT-20260926-0042",
  "algorithm": "Hybrid_QI_A5",
  "seed": 1005,
  "evaluations": 2500,
  "objective_profile": "balanced",
  "objectives": {
    "fuel_consumption_tonnes": 96.4,
    "operating_cost_usd": 104850.00,
    "lifecycle_ghg_wtw_tco2e": 246.20,
    "schedule_delay_hours": 0.0
  },
  "constraints": {
    "status": "FEASIBLE",
    "cargo_demand_satisfied": true,
    "schedule_limit_satisfied": true,
    "speed_bounds_satisfied": true,
    "fuel_compatibility_satisfied": true
  },
  "vessel_dispatch": [
    {
      "vessel_id": "CPS_Poseidon",
      "speed_kn": 14.2,
      "fuel": "vlsfo",
      "cargo_tonnes": 14200,
      "shore_power": true
    },
    {
      "vessel_id": "CPS_Triton",
      "speed_kn": 13.8,
      "fuel": "vlsfo",
      "cargo_tonnes": 8500,
      "shore_power": true
    },
    {
      "vessel_id": "OSS_Ceto",
      "speed_kn": 12.0,
      "fuel": "mgo",
      "cargo_tonnes": 3200,
      "shore_power": false
    }
  ],
  "decision_status": "APPROVED",
  "operator_note": "Approved slow-steaming speed profile with shore power cold-ironing active at Berth 4."
}
```

---

## 5. Scientific Claim Discipline & Evaluator Defense

When presenting this decision support architecture to SIH evaluators or maritime inspectors, the following strict factual boundaries must be maintained:

1. **Quantum-Inspired vs. Quantum Hardware**:
   - The optimization engines (QIEA and QPSO) execute strictly on **classical digital hardware** (x86_64 / ARM CPU).
   - They employ quantum-inspired mathematical representations (qubit rotation vectors, state superposition probabilities) to achieve high search diversity, but do **not** require quantum processing units (QPUs).
   - Never claim "quantum advantage", "quantum supremacy", or "exponential quantum speedup".

2. **Advisory Decision Support vs. Autonomous Control**:
   - EGREEN QUANTA is an **advisory decision-support system**.
   - It computes mathematically optimal and hydrodynamically feasible voyage plans for human evaluation.
   - It does **not** directly interface with engine throttles, steering governors, or shipboard automation systems without explicit human confirmation.

3. **Alternative Fuel Modeling vs. Field Measurements**:
   - Results for bio-methanol, liquid hydrogen, and green ammonia are **scenario estimates** based on invariant shaft work energy conversion ($1.0 \times \text{shaft energy equivalent}$ of VLSFO/MGO) and IMO MEPC.391(81) Well-to-Wake emission factors.
   - They must never be described as "measured hydrogen consumption" unless real physical fuel flow meter data is connected.
