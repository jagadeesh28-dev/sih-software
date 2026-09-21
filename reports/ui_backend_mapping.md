# Authoritative Backend Source Mapping: Egreen Quanta (SIH26138)

**Document Purpose**: Maps every UI display element, numerical KPI, and decision output directly to authoritative backend source files, functions, input/output schemas, engineering units, and deterministic failure states.

---

## 1. Authoritative Backend Mapping Table

### 1. Fuel Prediction (General Point Prediction)
- **UI Element**: Predicted Fuel Consumption KPI (`kg/h`)
- **API / Function**: `ProductionFuelPredictor.predict_fuel_with_uncertainty()`
- **Source File**: [`src/qi_prediction/serving.py`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/src/qi_prediction/serving.py#L225)
- **Input Schema**: `Dict[str, Union[float, str]]` containing `stw_kn`, `sog_kn`, `draft_m`, `displacement_t`, `wave_height_m`, `water_depth_m`, `vessel_type`, `fuel_type`.
- **Output Schema**: `Dict[str, Any]` with key `"fuel_prediction": float`.
- **Units**: $\text{kg/h}$ (kilograms per hour).
- **Failure State**: If inputs are physically invalid or missing mandatory dimensions, triggers `validate_and_sanitize_point()` -> hard input rejection; if booster crashes, routes to `PhysicsFuelPredictor` emergency output.

### 2. MODEL-REAL-04 (Reference Anchor Model)
- **UI Element**: Reference Anchor Cross-Check KPI & Fallback Model Badge
- **API / Function**: `ProductionFuelPredictor.model_real_04_booster.predict(df_m04)`
- **Source File**: [`src/qi_prediction/serving.py`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/src/qi_prediction/serving.py#L348) loading [`models/model_real_04.txt`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/models/model_real_04.txt)
- **Input Schema**: 14-feature DataFrame (`stw_kn`, `sog_kn`, `draft_m`, `displacement_t`, `wind_speed_ms`, `wind_direction_deg`, `wave_height_m`, `wave_period_s`, `wave_direction_deg`, `current_speed_ms`, `current_direction_deg`, `water_depth_m`, `vessel_type`, `fuel_type`).
- **Output Schema**: Float residual + $F_{\text{phys}}$.
- **Units**: $\text{kg/h}$.
- **Failure State**: If unavailable, falls back to `PhysicsFuelPredictor`.

### 3. QI-C1 (Original Quantum-Inspired Candidate)
- **UI Element**: Candidate Prediction (6 Features)
- **API / Function**: `ProductionFuelPredictor.qi_c1_booster.predict(df_qi)`
- **Source File**: [`src/qi_prediction/serving.py`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/src/qi_prediction/serving.py#L325) loading [`models/qi_c1.txt`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/models/qi_c1.txt)
- **Input Schema**: 6-feature DataFrame (`stw_kn`, `sog_kn`, `draft_m`, `wave_height_m`, `water_depth_m`, `fuel_type`).
- **Output Schema**: Float residual + $F_{\text{phys}}$.
- **Units**: $\text{kg/h}$.
- **Failure State**: Catches exception, logs warning, routes to `MODEL-REAL-04`.

### 4. QI-C1-vessel-type (Candidate with Explicit Vessel Conditioning)
- **UI Element**: Primary Serving Model for Vessel Predictions
- **API / Function**: `ProductionFuelPredictor.qi_c1_vessel_type_booster.predict(df_qi_vt)`
- **Source File**: [`src/qi_prediction/serving.py`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/src/qi_prediction/serving.py#L336) loading [`models/qi_c1_vessel_type.txt`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/models/qi_c1_vessel_type.txt)
- **Input Schema**: 7-feature DataFrame (`stw_kn`, `sog_kn`, `draft_m`, `wave_height_m`, `water_depth_m`, `vessel_type`, `fuel_type`).
- **Output Schema**: Float residual + $F_{\text{phys}}$.
- **Units**: $\text{kg/h}$.
- **Failure State**: If `vessel_type` is unsupported or unknown, routes to `MODEL-REAL-04` fallback.

### 5. Conformal Uncertainty Quantification
- **UI Element**: 90% and 95% Conformal Prediction Intervals `[Lower, Upper] kg/h` and MPIW
- **API / Function**: `ProductionFuelPredictor` conformal calibration layer
- **Source File**: [`src/qi_prediction/serving.py`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/src/qi_prediction/serving.py#L415) loading [`models/conformal_quantiles.json`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/models/conformal_quantiles.json)
- **Input Schema**: Coverage float (`0.90` or `0.95`), envelope distance $d_{\text{env}}$.
- **Output Schema**: `Dict[str, Union[float, bool]]` with `lower_bound_kg_h`, `upper_bound_kg_h`, `interval_width_kg_h`, `is_high_uncertainty`.
- **Units**: $\text{kg/h}$.
- **Failure State**: Dynamic scaling $q_{\text{scaled}} = q_{\text{base}} \cdot (1 + 0.5 \cdot \max(0, d_{\text{env}} - 0.5))$ flags `is_high_uncertainty = True`.

### 6. Out-of-Distribution (OOD) Detection
- **UI Element**: Convex Envelope Distance Gauge ($d_{\text{env}}$) and Domain Badge (`IN-DOMAIN`, `WARNING`, `OOD`)
- **API / Function**: `ProductionFuelPredictor.compute_envelope_distance()` & `prediction.domain_checker.DomainChecker`
- **Source File**: [`src/qi_prediction/serving.py`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/src/qi_prediction/serving.py#L202) loading [`models/domain_checker.json`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/models/domain_checker.json)
- **Input Schema**: Clean numerical telemetry dictionary.
- **Output Schema**: `(in_domain: bool, near_boundary: bool, envelope_distance: float)`.
- **Units**: Dimensionless distance metric ($0.0 \le d_{\text{env}} \le \infty$).
- **Failure State**: $d_{\text{env}} > 1.50$ triggers severe OOD alert and disallows normal recommendation.

### 7. Fallback Routing Policy
- **UI Element**: Model Routing State Badge (`NORMAL`, `FALLBACK`, `EMERGENCY_PHYSICS`)
- **API / Function**: `ProductionFuelPredictor` 3-tier routing logic
- **Source File**: [`src/qi_prediction/serving.py`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/src/qi_prediction/serving.py#L371)
- **Input Schema**: In-domain flags, envelope distance, cross-check delta ($|\hat{y}_{\text{QI}} - \hat{y}_{\text{M04}}|$).
- **Output Schema**: String enum: `"NORMAL"` / `"FALLBACK"` / `"EMERGENCY_PHYSICS"`.
- **Units**: Categorical state.
- **Failure State**: Automatically engages `MODEL-REAL-04` on discrepancy $> 500\text{ kg/h}$ or boundary distance $> 1.0$.

### 8. Vessel Type Canonical Encoding
- **UI Element**: Explicit Vessel Type Badge (`passenger_cruise`, `passenger_cruise_small`, `offshore_supply`)
- **API / Function**: `optimization.canonical_mapper.canonicalize_vessel_type()`
- **Source File**: [`optimization/canonical_mapper.py`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/optimization/canonical_mapper.py#L75)
- **Input Schema**: String vessel name or category alias.
- **Output Schema**: Standardized canonical string.
- **Units**: Categorical.
- **Failure State**: Unmapped vessel types map to `"passenger_cruise"` with an `unsupported_vessel_type` warning flag.

### 9. Operational Cost Engine
- **UI Element**: Itemized Cost Breakdown ($C_{\text{fuel}}, C_{\text{elec}}, C_{\text{OPS}}, C_{\text{carbon}}, C_{\text{sched}}, C_{\text{FuelEU}}$) & Total Cost
- **API / Function**: `SIHObjectiveEngine.evaluate_voyage()` & `FleetCostEngine.compute_leg_costs()`
- **Source File**: [`optimization/sih_objective_engine.py`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/optimization/sih_objective_engine.py#L138) & [`optimization/cost_model.py`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/optimization/cost_model.py)
- **Input Schema**: `fuel_mass_tonnes`, `fuel_type`, `ttw_co2_tonnes`, `voyage_duration_hours`, `schedule_deadline_hours`, `use_shore_power`, `port_hours`, `hotel_load_kw`.
- **Output Schema**: `SIHOptimizationObjectives` with `operational_cost_usd`, `fuel_cost_usd`, `shore_power_cost_usd`, `carbon_cost_usd`, `schedule_penalty_usd`, `fueleu_penalty_usd`.
- **Units**: $\text{USD}$ ($\$$).
- **Failure State**: If parameters missing, defaults to baseline demurrage $\$1,000/\text{h}$, ETS scope $100\%$, carbon $\$90/\text{t}$.

### 10. Lifecycle GHG Emissions Engine
- **UI Element**: Lifecycle Decomposition ($\text{WtW} = \text{WtT} + \text{TtW} + \text{Slip}$) in $\text{tCO}_2\text{e}$
- **API / Function**: `SIHObjectiveEngine.evaluate_voyage()` & `FleetEmissionsEngine.compute_leg_emissions()`
- **Source File**: [`optimization/sih_objective_engine.py`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/optimization/sih_objective_engine.py#L173) & [`optimization/emissions_model.py`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/optimization/emissions_model.py)
- **Input Schema**: `fuel_mass_kg`, `fuel_type` matching pathway registry.
- **Output Schema**: `Dict[str, float]` with `wtw_total_tonnes_co2e`, `wtt_tonnes_co2e`, `ttw_co2_tonnes`, `methane_slip_tonnes_co2e`.
- **Units**: $\text{tCO}_2\text{e}$ (tonnes $\text{CO}_2$ equivalent under IMO MEPC.391(81)).
- **Failure State**: Unknown fuel routes to conventional VLSFO emission factors with an audit flag.

### 11. Alternative Marine Fuel Pathways
- **UI Element**: Alternative Fuels Comparison Matrix & Stacked Decomposition
- **API / Function**: `lca.fuel_registry.FuelPathwayRegistry.convert_mass_by_lhv()`
- **Source File**: [`lca/fuel_registry.py`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/lca/fuel_registry.py) loading [`configs/fuels.yaml`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/configs/fuels.yaml)
- **Input Schema**: Baseline VLSFO mass, target fuel code (`fossil_lng`, `bio_methanol`, `green_ammonia`, `liquid_hydrogen`).
- **Output Schema**: Target equivalent mass $(\text{kg})$, energy content $(\text{MJ})$, LHV $(\text{MJ/kg})$.
- **Units**: Mass ($\text{t}$), Energy ($\text{MJ}$), Emissions ($\text{tCO}_2\text{e}$).
- **Failure State**: Missing pathway defaults to conventional VLSFO with mandatory warning.

### 12. Shore Power (Cold Ironing / OPS)
- **UI Element**: Cold Ironing at Berth Energy, Cost, and Grid Emission Callout
- **API / Function**: `FleetCostEngine` & `FleetEmissionsEngine` shore power modules
- **Source File**: [`optimization/sih_objective_engine.py`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/optimization/sih_objective_engine.py#L183) & [`configs/fuels.yaml`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/configs/fuels.yaml#L95)
- **Input Schema**: `use_shore_power: bool`, `port_hours: float`, `hotel_load_kw: float`.
- **Output Schema**: Electricity consumed $(\text{kWh})$, cost $(\$)$, grid emissions $(\text{tCO}_2\text{e})$.
- **Units**: $\text{kWh}$, $\$$, $\text{tCO}_2\text{e}$.
- **Failure State**: If disabled, berth emissions computed from auxiliary marine gas oil.

### 13. Fleet Multi-Objective Optimizer
- **UI Element**: Fleet Dispatch Solver Form, Weights, Decision Vector, Advisory Plan
- **API / Function**: `optimization.sih_objective_engine.SIHObjectiveEngine` & verified benchmarks
- **Source File**: [`optimization/sih_objective_engine.py`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/optimization/sih_objective_engine.py) & [`results/algorithm_multiobjective_results.csv`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/results/algorithm_multiobjective_results.csv)
- **Input Schema**: Objective weights $w_1, w_2, w_3, w_4$, algorithm choice (`DE`, `GA`, `QPSO`, `NSGA-III`), evaluation budget, seed.
- **Output Schema**: Optimal speed vector $[v_1^*, v_2^*, v_3^*]$, bunkering allocation, feasibility flag, total penalty.
- **Units**: $\text{knots}$, $\text{tonnes}$, $\text{USD}$, $\text{hours}$.
- **Failure State**: If constraints violated, penalty function inflates $J_{\text{pen}}$, blocking automated acceptance.

### 14. Pareto Front & Trade-Offs
- **UI Element**: Cost vs WtW GHG Interactive Scatter Plot with Fuel Point Sizing
- **API / Function**: `dashboard.backend_bridge.get_verified_pareto_front()`
- **Source File**: [`results/pareto_front.csv`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/results/pareto_front.csv) & [`results/multiobjective_tradeoffs.csv`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/results/multiobjective_tradeoffs.csv)
- **Input Schema**: Static CSV verified dataset (13 non-dominated solutions; 152 comparative runs).
- **Output Schema**: DataFrame with columns `formulation`, `seed`, `algorithm`, `is_feasible`, `fuel_tonnes`, `cost_usd`, `ghg_tonnes`, `delay_hours`.
- **Units**: $\text{USD}$ ($X$-axis), $\text{tCO}_2\text{e}$ ($Y$-axis), $\text{tonnes}$ (point size).
- **Failure State**: If file unreadable, renders error notice.

### 15. Demo Scenarios Suite
- **UI Element**: Demo Center 11-Scene Verification Walkthrough
- **API / Function**: `scripts.demo_scenarios.run_all_demo_scenes()` logic
- **Source File**: [`scripts/demo_scenarios.py`](file:///c:/Users/JAGADEESH%20M/OneDrive/Documents/SIH-software/sih26138_platform/scripts/demo_scenarios.py)
- **Input Schema**: Discrete scene selector (Scenes 1 to 11).
- **Output Schema**: Verbatim jury verification cards with exact certified numbers and timing markers.
- **Units**: Scenario-dependent ($\text{kg/h}$, $\text{kn}$, $\text{t}$, $\$$).
- **Failure State**: Watermarked visibly with `[DEMO / SIMULATION MODE]`.
