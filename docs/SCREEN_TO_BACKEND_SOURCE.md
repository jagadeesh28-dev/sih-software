# Screen → API → Backend Source Map

The frontend (`web/`) computes no scientific values. Every number it shows comes from one of the API endpoints below.

## Provenance labels shown in the HMI

| Label | Meaning |
|---|---|
| MODEL OUTPUT | Computed on request by the backend |
| MEASURED | Row of the recorded FuelCast dataset (historical, not live) |
| ASSUMED | Fleet default operating state |
| SCENARIO INPUT / SCENARIO ESTIMATE | Operator what-if inputs and their outputs |
| STORED ARTIFACT / HISTORICAL EVIDENCE | Committed repository file |

## Map

| Screen | Endpoint(s) | Backend module(s) | Values & provenance |
|---|---|---|---|
| Top bar / status bar | `GET /api/status` | `api.main.status`; `src/qi_prediction/serving.py`; `common/fleet_defaults.py`; SQLite ledger | mode (no live feed), fleet trust (MODEL OUTPUT), dataset end dates (MEASURED), last recommendation (ledger) |
| Fleet Overview | `GET /api/fleet` | `ProductionFuelPredictor.predict_fuel_with_uncertainty`; `SIHObjectiveEngine.evaluate_voyage` | states ASSUMED; fuel + interval MODEL OUTPUT; cost/GHG per hour SCENARIO ESTIMATE; schedule NOT TRACKED |
| Vessel Detail | `GET /api/vessels/{id}` | predictor; parquet replay (`data/processed/real/fuelcast/*.parquet`) | prediction MODEL OUTPUT; latest record + trend MEASURED (dataset replay) |
| Prediction & Trust | `POST /api/predict` | predictor router: validation → L∞ envelope guard → boosters → conformal interval | all MODEL OUTPUT; trust state from `classify_trust` (mapping only) |
| Scenario Lab | `POST /api/scenario` | predictor + `SIHObjectiveEngine`; `configs/fuels.yaml` | per-field MEASURED / ASSUMED / SCENARIO INPUT; results SCENARIO ESTIMATE |
| Fleet Optimizer | `GET /api/optimizer/config`, `POST /api/optimize`, `GET /api/optimize/{id}`, `POST /api/recommendations/{id}/decision` | `optimization/fleet_evaluator_phase4.py`, `src/evaluator/common_evaluator.py`, `src/algorithms/*` | live MODEL OUTPUT; decision → ledger |
| Pareto / Trade-offs | `GET /api/pareto`, `POST /api/pareto/{id}/resolve` | `results/pareto_front.csv` (STORED ARTIFACT from `scripts/run_multiobjective_tradeoffs.py::run_pareto_search`) | stored plans with full decision vector; resolve re-evaluates the vector with `Phase4FleetEvaluator` and returns a reproduced flag |
| Alternative Fuels | `GET /api/fuels` | predictor (VLSFO basis) + `SIHObjectiveEngine`; `configs/fuels.yaml` | VLSFO row MODEL OUTPUT; all others SCENARIO ESTIMATE (never measured) |
| Alerts & Safety | `GET /api/alerts` | fleet evaluation + session ledger | states from backend; explanations are UI copy |
| Audit / Reports | `GET /api/audit` | SQLite ledger `data/runtime/hmi_audit.sqlite`; `RELEASE/*.json`; artifact SHA-256 | current session / prior sessions / HISTORICAL EVIDENCE |
| Demo Mode | `GET /api/demo/scenes`, `POST /api/demo/scenes/{n}` | scene inputs from `scripts/demo_scenarios.py`; live backend | DEMO / SIMULATION |

## Two domain guards, two purposes

| Guard | Where | Purpose | Decision rule |
|---|---|---|---|
| Serving OOD guard | `src/qi_prediction/serving.py` | Operator trust for a single prediction | worst supplied-feature exceedance in training spans: > 1.0 WARNING + MODEL-REAL-04, > 1.5 OOD (physics emergency, "not a recommendation"), > 3.0 REJECT |
| Optimizer domain checker | `prediction/domain_checker.py` via each vessel's `SafeFuelObjective` | Feasibility of optimizer candidates | any feature outside its per-vessel training [min, max] → OUT_OF_DOMAIN → hard violation (infeasible); outside P01–P99 → NEAR_BOUNDARY |

The optimizer rule is stricter (zero tolerance beyond its per-vessel training range). Verified on 2026-09-24 across all 1,248 states it accepts over 3 vessels × 4 weather scenarios × a speed sweep: the maximum serving-guard distance is **0.101**, inside the IN_DOMAIN band (≤ 1.0). So an optimizer plan cannot fall into the serving WARNING, OOD or REJECT bands. This is regression-tested in `tests/test_api.py::test_optimizer_domain_is_inside_serving_envelope`. The RMS distance that `DomainChecker` reports is diagnostic only and is never used for its decision.

**Defect fixed 2026-09-24:** the optimizer's calibration-grid fast path set `domain_status = "VALID"` without running the checker. Plans at out-of-domain speeds (e.g. CPS_Triton 18.0 kn, OSS_Ceto 15.0 kn) were therefore reported feasible. The grid path now runs `DomainChecker.evaluate_point` on the actual operating state. Optimizer results produced before the fix are archived in `results/superseded/2026-09-24_pre_optimizer_domain_fix/`.

**Pareto screen (after the 2026-09-24 investigation):** the one-point front was caused by a formulation loophole (a vessel in `port`/`dp` mode "completed" an assigned voyage) plus a non-functional NSGA-III. Both are fixed; `results/pareto_front.csv` holds feasible, penalty-free, non-dominated plans from a true multi-objective NSGA-III search, matching an exhaustive grid of the valid decision space (31 plans after the shore-power correction; the earlier 6-point front is superseded). Details: `docs/OPTIMIZER_PARETO_INVESTIGATION.md`, `docs/SHORE_POWER_CORRECTION.md`.

**Berth accounting (both engines, `optimization/berth_model.py`):** shore power ON = grid electricity cost + grid GHG; OFF = onboard generator fuel (cost, ETS, WtW) in the selected pathway. The Alternative Fuels screen shows the per-pathway shore-vs-onboard comparison computed by `/api/fuels` (`shore_comparison`); the Scenario Lab shows the berth source, energy, fuel and GHG from `/api/scenario`.
