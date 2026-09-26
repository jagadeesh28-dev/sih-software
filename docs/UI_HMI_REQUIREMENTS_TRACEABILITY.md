# UI / HMI Requirements Traceability — Egreen Quanta (SIH26138)

**Specification traced:** the "EGREEN QUANTA UI transformation" brief, which covers the global HMI, 10 screens, human-in-the-loop, state management, responsiveness and migration. No separate master-requirements file exists in the repository; this matrix uses that brief's wording.

**Legend.** Status is one of:
- **MET** — implemented and verified.
- **MET (LIMITED)** — implemented, with a stated data limit.
- **N/A** — not implementable truthfully; the reason is given.

**Test references:**
- `API:` — `tests/test_api.py`
- `E2E:` — `tests/test_ui_failure_and_e2e.py`
- `GUARD:` — `tests/test_ood_guard.py`
- `FE:` — `web/src/**/*.test.ts(x)`
- `BROWSER` — manual Chrome DevTools verification at 1366×768 and 1920×1080, recorded in `docs/FINAL_RELEASE_STATUS.md`

## Global HMI

| Requirement | Component | API endpoint | Backend source of truth | Test | Status |
|---|---|---|---|---|---|
| Top bar: EGREEN QUANTA, mode, fleet count, active vessel, model ID, scenario, timestamp | `components/hmi/app-shell.tsx` `TopBar` | `GET /api/status` | `api.main.status` → serving predictor, `common/fleet_defaults.py` | API `test_status_reports_no_live_feed`; BROWSER | MET |
| LIVE / SIMULATION / DEMO mode | `ModeSwitch` | `GET /api/status` (`live_feed_connected`) | no live feed exists → LIVE disabled | API `test_status_reports_no_live_feed`; BROWSER | MET — LIVE is visibly disabled |
| Left navigation, 10 screens | `SideNav` | — | — | BROWSER (all routes return 200) | MET |
| Bottom status: data freshness, model state, OOD, fallback, last recommendation | `StatusBar` | `GET /api/status` | dataset last timestamps; `fleet_trust`; SQLite ledger | BROWSER | MET — freshness is "NO LIVE FEED + dataset end date" |
| Explicit units (kg/h, kn, t, tCO2e, MJ/h, USD, h) | `lib/hmi.ts` `UNITS` | — | — | BROWSER | MET |
| Never colour alone | `StateBadge`, `ToneChip` (icon + text) | — | — | FE `StateBadge always renders a text label` | MET |
| Loading / empty / error states | `DataState`, `Loading`, `Empty`, `ErrorBox` | all | — | FE `DataState …` (3 tests); BROWSER with API stopped | MET |
| OOD / fallback / invalid-input states | `TrustBanner`, `StateBadge` | `/api/predict` etc. | serving router → `classify_trust` | API, E2E, GUARD | MET |
| Keyboard access, visible focus, skip link | `globals.css :focus-visible`, `app-shell` skip link | — | — | BROWSER (Tab shows focus ring) | MET |
| 1366×768 and 1920×1080 | grid layouts with `minmax(0,1fr)` | — | — | BROWSER | MET |
| Typed API contracts, validated responses | `lib/api.ts` (zod) | all | — | FE `rejects a response that violates the contract` | MET |
| No scientific formulas in TypeScript | all pages | — | — | provenance scan (FINAL_RELEASE_STATUS §Provenance) | MET |

## 1. Fleet Overview (`app/fleet/page.tsx`)

| Requirement | API | Source of truth | Test | Status |
|---|---|---|---|---|
| Per-vessel name, type, speed, fuel | `GET /api/fleet` | `common/fleet_defaults.py` (ASSUMED) | API `test_fleet_predictions_come_from_backend` | MET |
| Predicted fuel + uncertainty interval | `/api/fleet` | serving predictor + conformal quantiles | same | MET |
| OOD status, fallback status | `/api/fleet` → `trust` | `classify_trust` | same | MET |
| Schedule status | `/api/fleet` (`schedule: null`) | no schedule feed | same | N/A — shown as "NOT TRACKED", never invented |
| Fleet KPIs: fuel, cost, lifecycle GHG | `/api/fleet` `kpis` | predictor; SIH engine at configured prices | same | MET (cost/GHG labelled SCENARIO ESTIMATE per hour) |
| Alerts: OOD, missing telemetry, fallback, constraint violations | derived from `trust` | `classify_trust` | API alerts test | MET — constraint violations appear after an optimizer run |
| Actions: Open Vessel, Run Scenario, Optimize Fleet | links / router | — | BROWSER | MET |

## 2. Vessel Detail (`app/vessel/[id]/page.tsx`)

| Requirement | API | Source of truth | Test | Status |
|---|---|---|---|---|
| Identity, type, model version, route | `GET /api/vessels/{id}` | fleet defaults; model meta | BROWSER | MET (route = ASSUMED) |
| STW/SOG, draft/loading, weather, wave, depth, fuel type | same | fleet defaults (ASSUMED) and latest dataset record (MEASURED) | BROWSER | MET |
| Prediction kg/h, bounds, confidence, timestamp | same | serving predictor | BROWSER | MET |
| Trust: IN-DOMAIN / WARNING / OOD / FALLBACK | same | `classify_trust` + envelope gauge | BROWSER | MET |
| Time/trend from actual data | same (`trend`) | FuelCast parquet replay, observed vs served prediction | BROWSER | MET — labelled DATASET REPLAY, not live |
| No invented feature importance; show actual model inputs | same (`model_features`) | booster feature list | BROWSER | MET |

## 3. Prediction & Trust (`app/trust/page.tsx`)

| Requirement | API | Source of truth | Test | Status |
|---|---|---|---|---|
| Model ID, prediction, confidence, interval | `POST /api/predict` | serving router | API `test_predict_normal_invalid_and_unsupported_vessel` | MET |
| OOD state + reason (dominant feature named) | same | L∞ envelope guard | GUARD all; API `test_storm_is_never_normal` | MET |
| Fallback explicit "MODEL-REAL-04 FALLBACK" | same | router FALLBACK route | API (near-boundary draft 13.5 m) | MET |
| Data validity, input completeness | same | serving contract; missing-factor list | API; BROWSER | MET |
| OOD never resembles normal; physics value "NOT A RECOMMENDATION" | `TrustBanner`, `PredictionReadout` | — | BROWSER (storm, draft 22 m) | MET |

## 4. Scenario Lab (`app/scenario/page.tsx`)

| Requirement | API | Source of truth | Test | Status |
|---|---|---|---|---|
| Inputs: vessel, speed, draft/loading, weather, fuel, shore power, distance, deadline | `POST /api/scenario` | predictor + SIH objective engine | API `test_scenario_provenance_and_validation` | MET |
| Vessel type input | fixed by the chosen vessel | trained categories | — | MET (LIMITED) — type follows the vessel |
| Duration | derived by the engine from distance / speed | SIH engine | same | MET (LIMITED) — not a free input |
| Cargo | `unsupported_inputs` | voyage engine has no cargo term | same | N/A in the voyage engine — shown disabled and pointing to the Fleet Optimizer |
| MEASURED / ASSUMED / SCENARIO INPUT per field | same (`provenance`) | API provenance map | same | MET |
| Results: fuel, cost, lifecycle GHG, schedule, feasibility | same | SIH engine | same | MET |
| Assumptions and configuration metadata (fuels.yaml + sha256) | same | `configs/fuels.yaml` | same | MET |

## 5. Fleet Optimizer (`app/optimizer/page.tsx`)

| Requirement | API | Source of truth | Test | Status |
|---|---|---|---|---|
| Connects to the real optimizer; progress = real evaluation counter | `POST /api/optimize`, `GET /api/optimize/{id}` | `Phase4FleetEvaluator` + DE/GA/NSGA-III/QPSO | API `test_optimizer_job_and_human_decision` | MET |
| Decision variables: demand/vessel assignment, cargo, speed, fuel, shore power | job `result.vessels` | evaluator decoding | same | MET |
| Vessel mix | fixed 3-vessel fleet; assignment is the decision | `FLEET_VESSELS` | — | MET (LIMITED) |
| Objectives: fuel, OPEX, WtW GHG, schedule, risk | job `result.objectives` | evaluator | same | MET |
| Constraints (cargo, capacity, speed, schedule, fuel compatibility, domain) | `/api/optimizer/config` `constraints_doc`; `hard_violations` | evaluator + DomainChecker (grid path fixed) | E2E, phase4/phase5 suites | MET |
| Algorithm, seed, budget, feasibility, objective vector, selected plan | job payload | optimizer | same | MET |
| "ADVISORY — REQUIRES HUMAN ACCEPTANCE"; PENDING REVIEW → ACCEPT/REJECT with confirmation | `POST /api/recommendations/{id}/decision` | API state + SQLite ledger | same (409 on double decision) | MET |

## 6. Pareto / Trade-offs (`app/pareto/page.tsx`)

| Requirement | API | Source of truth | Test | Status |
|---|---|---|---|---|
| Cost vs lifecycle GHG chart, feasible only, no duplicates | `GET /api/pareto` | `results/pareto_front.csv` (NSGA-III multi-objective search; feasible, penalty-free, non-dominated; see docs/OPTIMIZER_PARETO_INVESTIGATION.md) | API `test_pareto_is_feasible_and_deduplicated`, `test_pareto_summary_states_point_count_without_ranking`; `tests/test_pareto_contract.py` | MET — 31 non-dominated plans (symmetric berth accounting, 2026-09-24); the summary line states the count and never ranks a best |
| Click exposes ID, speeds, fuel, cargo, cost, GHG, schedule, decision variables | `POST /api/pareto/{id}/resolve` | stored decision vector re-evaluated by the live evaluator (no optimizer re-run) | API `test_pareto_resolve_reproduces_archive`; `tests/test_pareto_contract.py::test_stored_front_contract` | MET |
| No "BEST" label | page | — | BROWSER | MET |

## 7. Alternative Fuels (`app/fuels/page.tsx`)

| Requirement | API | Source of truth | Test | Status |
|---|---|---|---|---|
| VLSFO, MGO, LNG, Bio-Methanol, Green Ammonia, LH2, shore power | `GET /api/fuels` | `configs/fuels.yaml` pathways + shore-power variant | API `test_fuels_are_labelled_and_energy_invariant` | MET |
| Fuel rate, cost, lifecycle GHG, assumptions, config source | same | SIH engine; registry | same | MET |
| "SCENARIO ESTIMATE — NOT MEASURED GREEN-FUEL TELEMETRY" (prominent) | page banner + per-row chips | `measured_telemetry: false` | same; BROWSER | MET |

## 8. Alerts & Safety (`app/alerts/page.tsx`)

| Requirement | API | Source of truth | Test | Status |
|---|---|---|---|---|
| States: NORMAL, WARNING, OOD, FALLBACK, INVALID INPUT, MISSING FACTOR, CONSTRAINT FAILURE, RUNTIME FAILURE | `GET /api/alerts` | fleet evaluation + session ledger | API alerts + demo scene 6 tests | MET |
| Explanation, operator action, source, timestamp | page + `lib/hmi.ts STATE_META` (UI copy) | — | BROWSER | MET |
| OOD more prominent than normal | critical cards (red, `role=alert`) | — | BROWSER | MET |

## 9. Audit / Reports (`app/audit/page.tsx`)

| Requirement | API | Source of truth | Test | Status |
|---|---|---|---|---|
| Real session records only (no fake history) | `GET /api/audit` | SQLite ledger `data/runtime/hmi_audit.sqlite` | API `test_audit_events_are_persisted_to_sqlite` | MET |
| Timestamp, scenario, vessel, type, inputs, model, version, prediction, uncertainty, OOD, fuel scenario, price config, lifecycle config hash, optimizer, seed, budget, selected solution, accept/reject, warnings, fallbacks | event payload + indexed columns | `api.main.record` | same | MET |
| Pareto alternatives in the audit | Pareto screen (stored artifact) | `results/pareto_front.csv` | — | MET (LIMITED) — alternatives are not copied into each event |
| CURRENT SESSION vs HISTORICAL EVIDENCE (and PRIOR SESSIONS) | three panels | ledger session_id; RELEASE artifacts | API `test_prior_sessions_are_separated_from_current_session` | MET |
| No false immutability claim | labels | "append-only, not cryptographically sealed" | same | MET |

## 10. Demo Mode (`app/demo/page.tsx`)

| Requirement | API | Source of truth | Test | Status |
|---|---|---|---|---|
| Deterministic verified scenes (normal, high demand, slow steaming, fuels, OOD storm, runtime failure, fleet optimization, plus 4 more) | `GET/POST /api/demo/scenes` | `scripts/demo_scenarios.py` constants; live backend | API `test_demo_scenes_run_on_backend[1-11]`; `demo_scenarios.py` 11/11 | MET |
| "DEMO MODE · SIMULATION", never resembles live | banner, purple frame, top-bar mode | — | BROWSER | MET |
| Values from backend only | payloads re-validated with shared schemas | — | FE contract test; ErrorBoundary | MET |

## Human-in-the-loop

| Requirement | Implementation | Test | Status |
|---|---|---|---|
| PENDING REVIEW / ACCEPT / REJECT | job `recommendation_status`; decision endpoint | API optimizer test (409 on repeat) | MET |
| Critical actions require confirmation | `components/hmi/confirm.tsx` (AlertDialog) | BROWSER | MET |
| No vessel or engine actuation | the API has no actuation endpoint; each decision is recorded with `actuation: NONE` | code inspection | MET |

## Migration

| Requirement | Status |
|---|---|
| Parity verified before deprecation | MET — prediction, uncertainty, OOD, fallback, scenario, optimizer, Pareto and demo all verified via the API |
| Streamlit UI removed; backend preserved | MET — `dashboard/`, `streamlit` and `plotly` removed; all scientific modules kept |
