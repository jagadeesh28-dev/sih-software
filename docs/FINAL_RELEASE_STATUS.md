# Final Release Status — SIH26138 Egreen Quanta

**Date:** 2026-09-24 · **Base commit:** 0804bf2 (plus uncommitted release-freeze and optimizer-investigation changes)

## Decision

**RELEASE CANDIDATE — MODELING ISSUE REMAINS** (shore-power defect corrected; see `docs/SHORE_POWER_CORRECTION.md`)

Remaining issue: **MGO is declared compatible for OSS_Ceto but cannot be encoded by the fuel gene** (`FUEL_MAP` has no `mgo`). The stored front is therefore the exact non-dominated set of the *encodable* decision space, not of the declared one. On the Alternative Fuels screen MGO costs more than VLSFO and emits less, so it could add Pareto plans. Fixing it re-indexes the fuel gene and needs full regeneration; it was deliberately excluded from this correction.

- Release gate: **16 / 16** on regenerated post-correction evidence (G7/G8 strengthened with berth-symmetry checks)
- pytest: **235 passed, 0 failed**
- Frontend: 11 / 11
- Demo: **11 / 11**
- `reproduce_release`: **10 / 10** (31/31 stored Pareto plans re-evaluated identically)

The berth phase is now modelled symmetrically in both engines: shore power pays electricity and grid emissions, while onboard generation burns the selected fuel. The corrected Pareto front has **31** plans, matching the exhaustive grid structurally. The previous 6-point front is superseded (`results/superseded/2026-09-24_pre_shore_power_correction/`).

## Optimizer investigation (2026-09-24)

The single-point Pareto front was **not** scientifically correct. Full report: `docs/OPTIMIZER_PARETO_INVESTIGATION.md`.

| Defect | Fix |
|---|---|
| Optimizer grid fast path skipped the domain check | runs `DomainChecker.evaluate_point` (earlier today) |
| `port` / `dp` mode "completed" an assigned voyage in 1–2 h (PS-01 was this) | hard constraint in the decoder |
| Cargo gene was dead yet displayed (0 t on a 1,200 t demand) | carried cargo = assigned demand quantity; gene documented as inert |
| NSGA-III never updated its population (random search) | rewritten on pymoo NSGA-III: reference directions, constraint-domination on penalty |
| Archives admitted soft-penalised plans | only feasible, penalty-free plans are archived |
| Front built from scalarised run-ends | front = non-dominated penalty-free archive of a multi-objective search, stored with full decision vectors |
| Trade-off demonstrations were penalised DE plans (22 h delay, labelled feasible) | selected from the verified front by stated rules |
| Optimizer screen labelled a fast-path placeholder vector as MODEL OUTPUT | API returns no objectives for unsimulated plans; UI shows "Not simulated" |
| Optimizer screen showed soft-penalised plans as plain "FEASIBLE" | `PlanStatus`: PENALTY-FREE / SOFT PENALTIES / CONSTRAINT FAILURE |
| `/api/optimize` rejected an algorithm that `/api/optimizer/config` offered | request model lists every offered algorithm; regression test added |
| `reproduce_release` step 8 passed on the pre-fix Phase 5 artifact | step 8 re-evaluates the post-fix front; Phase 5 labelled PRE-FIX HISTORICAL |

**Result (after the shore-power correction).** `results/pareto_front.csv` holds **31 non-dominated, feasible, penalty-free plans**, from $173,942.50 / 742.45 tCO2e to $442,810.01 / 617.92 tCO2e. They are identical in fuel mix and shore-power pattern to the 31 non-dominated plans of an exhaustive 124,416-candidate grid. (Before the correction: 6 plans, superseded.) No constraint was relaxed and no gate or test was weakened; G9 and scene 11 gained stricter checks.

## Evidence classes

### FRESHLY COMPUTED (2026-09-24)
- Release gate G1–G3, G5–G8, G12–G16 (`RELEASE/release_gate.json`).
- OOD guard matrix (G6); 1,000 invalid inputs + 19 edge cases (G12), 100 % safe rejection.
- POST-FIX optimizer evidence (`scripts/run_multiobjective_tradeoffs.py`):
  - `multiobjective_tradeoffs.csv` (5 formulations × 30 seeds, DE);
  - `algorithm_multiobjective_results.csv` (5 algorithms × 30 seeds, with penalty-free and non-dominated counts);
  - `pareto_front.csv`, `pareto_search_runs.csv`, `tradeoff_scenarios.csv`, `convergence_results.csv`, `cost_objective_results.csv`, `ghg_objective_results.csv`.
- Decision-space diagnostic: `results/diagnostics/pareto_space_summary.json`, `pareto_space_grid.csv`.
- `reproduce_release` step 8: 31/31 stored plans re-evaluated feasible, penalty-free and identical.
- Optimizer-domain vs serving-guard consistency: max serving distance 0.101 over 1,248 optimizer-accepted states.

### REFERENCE / HISTORICAL
- **PRE-FIX HISTORICAL:** Phase 5 frozen benchmark (825k evaluations; claim C-07); `results/superseded/2026-09-24_pre_optimizer_domain_fix/`. Not used as current evidence.
- G4, G9, G10 and G11 verify stored CSVs; they are not recomputed inside the gate. G9/G10 CSVs were regenerated today.

### LIMITATION (not a safety-contract violation)
- Berth model assumptions: SFOC 0.220 kg/kWh VLSFO-eq, auxiliaries burn the selected fuel, 2 h berth per demand in the fleet scenario, FuelEU on the sea passage only.
- Synthetic OOD test populations; the dataset has no real storm telemetry.
- Marginal-feature (axis-aligned L∞) OOD guard: joint anomalies with each feature in range are not detected.
- A weather-only storm (wind 45 m/s, Hs 14 m) gives d = 1.46: WARNING + MODEL-REAL-04 fallback, not OOD. It is flagged and never NORMAL; Hs 16 m gives OOD.
- The optimizer DomainChecker is intentionally separate from the serving guard and stricter than it.
- **Scalarised runs are weight-insensitive.** Soft penalties (thousands) swamp the normalised objectives (about 1–3), and random-initialised scalar optimizers spend most of the 2,500-evaluation budget reaching feasibility. All five formulations therefore return identical plans. The multi-objective front, not weighted runs, is the trade-off evidence.
- A single live optimizer run (Optimizer screen, scene 7) is a budget-limited scalar search. It is penalty-free but can be dominated by a front plan (A5 seed 1005 is dominated by PS-01).
- Fuel does not depend on cargo load (design displacement is used).
- **MGO (open modelling/encoding issue):** compatible with Ceto but not encodable; the front may be missing MGO trade-offs (see Decision).
- G11 "scalability" times a synthetic function, not the evaluator; no claim relies on it.
- Audit ledger is append-only through the API but not cryptographically sealed; the operator is unauthenticated.
- Schedule progress and live telemetry are not tracked (no feed).

## Optimizer comparison (post-fix, random init, 30 seeds × 2,500 evaluations)

| Algorithm | Final plan penalty-free | Runs that found any penalty-free plan | Median non-dominated per run |
|---|---|---|---|
| Hybrid QI A5 (with repair) | 30/30 | 30 | 5 |
| NSGA-III (pymoo) | 26/30 | 26 | 6.5 |
| QPSO | 10/30 | 10 | 0 |
| DE | 3/30 | 3 | 0 |
| Classical GA | 1/30 | 1 | 0 |

A5's lead is attributed to its repair operator on this 3-vessel instance; no broader claim is made.

## Safety (live API)

| Case | Result |
|---|---|
| Normal Poseidon | WARNING (interval width), IN_DOMAIN d=0 |
| Storm, weather only (wind 45, Hs 14) | WARNING, NEAR_BOUNDARY d=1.461, MODEL-REAL-04 FALLBACK |
| Storm, Hs 16 | OOD d=1.813, `PHYSICS EMERGENCY FALLBACK — NOT A RECOMMENDATION` |
| Demo storm (scene 5) | OOD / REJECT d=3.278, no prediction |
| Displacement 110,000 t | OOD d=1.889, `… NOT A RECOMMENDATION` |
| Hs 25 m | INVALID_INPUT |
| Unknown vessel type | OOD / CATEGORICAL, no prediction |
| Missing vessel type / speed | INVALID_INPUT |
| Runtime failure (scene 6) | `MODEL-REAL-04 FALLBACK` |

## Regression results (final)

| Check | Result |
|---|---|
| Backend pytest | **235 passed, 0 failed** (incl. 8 deterministic shore-power tests) |
| Frontend vitest | 11 / 11 |
| TypeScript / ESLint | clean / clean |
| `next build` | success |
| Demo scenes | 11 / 11 (scene 7 is a live post-fix run; scene 11 has the stricter checks) |
| Release gate | **16 / 16 — SIH26138 CORE REQUIREMENTS COMPLETE** |
| `reproduce_release.py` | 10 / 10 (8 freshly reproduced, 2 reference); optimizer 31/31 |
| Claims scan (G15) | pass; C-12 VERIFIED with post-fix evidence, C-14 updated, C-07 PRE-FIX HISTORICAL |
| Browser | Pareto screen: 31 points, summary line, PS-05 reproduced. Alternative Fuels: berth column plus a shore-vs-onboard panel with model-signed results (VLSFO shore −3.95 t; green NH3 shore +3.39 t). Optimizer: Hybrid QI A5 → "FEASIBLE — PENALTY-FREE" |

## Startup

```
.venv\Scripts\python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
cd web && npm run build && npm run start      # then open http://localhost:3000
```

Regenerating optimizer evidence (about 6 minutes): `.venv\Scripts\python scripts\run_multiobjective_tradeoffs.py`. The decision-space diagnostic (about 2 minutes): `.venv\Scripts\python scripts\diagnose_pareto_space.py`.
