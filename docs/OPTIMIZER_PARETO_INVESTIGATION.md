# Optimizer / Pareto Investigation (2026-09-24)

**Question:** after the optimizer-domain fix, the stored Pareto front held one plan (PS-01). Is that scientifically correct, or is another defect collapsing it?

> **Update (same day): superseded by the shore-power correction.** The 6-point front below was computed with an asymmetric berth model (shore power charged, onboard berth fuel never counted). With symmetric berth accounting the front has **31** plans; see `docs/SHORE_POWER_CORRECTION.md`. The defect analysis below (stationary modes, inert cargo, NSGA-III) remains valid.

**Answer:** it was a defect. PS-01 was not a physical plan. Once two formulation holes and one algorithm defect were fixed, the valid decision space contains **6 non-dominated, penalty-free plans**. An exhaustive grid and a corrected NSGA-III both find them independently.

Evidence: `scripts/diagnose_pareto_space.py` produces `results/diagnostics/pareto_space_grid.csv` and `results/diagnostics/pareto_space_summary.json`. `results/pareto_front.csv` and `results/pareto_search_runs.csv` come from `scripts/run_multiobjective_tradeoffs.py`. Contract tests are in `tests/test_pareto_contract.py`.

## 1. Formulation (as implemented)

**Decision vector:** 6 genes per vessel, for 3 vessels (18 dimensions); see `optimization/fleet_heterogeneous.py`.

| Gene | Bounds | Decoding |
|---|---|---|
| 0 demand | [0, 3] | round; 0 = unassigned, 1–3 = DEMAND-A/B/C |
| 1 cargo t | [0, DWT] | **inert** (see §3) |
| 2 speed kn | [min, max] of vessel | continuous; Poseidon 8–22, Triton 6–18, Ceto 4–15 |
| 3 fuel | [0, 4] | round; vlsfo, fossil_lng, bio_methanol, green_ammonia, liquid_hydrogen (mgo is not encodable) |
| 4 mode | [0, 3] | round; transit, maneuvering, dp, port |
| 5 shore power | [0, 1] | ≥ 0.5 |

**Compatibility:**
- Fuels: Poseidon {vlsfo, fossil_lng, bio_methanol}; Triton {vlsfo, bio_methanol}; Ceto {vlsfo, mgo, bio_methanol, green_ammonia}.
- Demand families: A → passenger_cruise; B → passenger_cruise or passenger_cruise_small; C → deck-cargo capable.
- Exactly-once assignment of each demand. With these compatibilities the only valid assignment is Poseidon→A, Triton→B, Ceto→C.

**Hard constraints** (→ infeasible):
- incompatibility: 100,000;
- duplicate demand: 100,000 per extra vessel;
- unfulfilled demand: 50,000;
- surrogate OUT_OF_DOMAIN in any weather scenario: 50,000;
- non-positive speed;
- **new:** a stationary mode on an assigned leg (§3).

**Soft penalties** (the plan stays "feasible"):
- actual speed after weather loss outside the vessel band: 5,000 per vessel-scenario;
- schedule delay: 500 per hour.

**Objectives:** probability-weighted over 4 weather scenarios. The vector is [fuel t, OPEX $, WtW GHG t, delay h, CVaR excess]. Scalar fitness = E[weighted normalised loss] + λ·(CVaR₀.₈ − E) + penalties.

**Selection:** Deb feasibility-first (feasible beats infeasible; then penalised fitness; then constraint violation). No repair is used in DE, GA, QPSO or NSGA-III. Hybrid QI A5 uses `FleetSolutionRepairer`.

**Termination:** a fixed evaluation budget (2,500 per run in the benchmark; 10,000 per seed in the Pareto search).

## 2. Root cause of the single-point front

1. **Stationary-mode loophole (formulation bug).**
   - `operating_mode` was a free gene. In `port` mode a leg took 2 h at 0 kn and in `dp` 1 h at 0.5 kn, regardless of distance.
   - An assigned 550 nm voyage could therefore be "completed" burning only hotel fuel.
   - The only consequence was the 5,000-per-scenario `speed_bound` soft penalty, and the plan remained `is_feasible=True`.
   - PS-01 was exactly this: CPS_Poseidon was on DEMAND-A in port mode. Its fitness of 23,947 was a 20,000 speed-band penalty plus 3,945 of delay penalty. It was neither physical nor penalty-free, and its "100.5 t fleet fuel" dominated every real plan.
2. **Front extraction took each scalarised run's final best.** Those plans carried soft penalties because "feasible" only meant "no hard violation".
3. **NSGA-III was not NSGA-III (algorithm bug).**
   - `src/algorithms/nsga3.py` bred every generation from the initial random population and never replaced it.
   - It had no non-dominated sorting, no reference directions and no survivor selection.
   - Its archive used only [fuel, OPEX] and admitted penalised plans.
4. **Penalty magnitude swamps the objectives (formulation property; not changed).** Soft penalties (thousands) are 3–4 orders of magnitude above the normalised objectives (about 1–3). Scalarised runs therefore minimise penalties, not the weighted objectives: all five formulations A–E return identical results for every seed (`results/multiobjective_tradeoffs.csv`).

## 3. PS-01 cargo allocation: 0 t on a 1,200 t demand

Classification: **C + G.** The demand-tonnage constraint was incomplete and the cargo gene was dead.
- The decoder only bounds the gene to [0, DWT].
- Nothing links it to the demand quantity, and it enters no fuel, cost, emission or displacement term (the fuel model uses design displacement).
- The formulation's exactly-once assignment already implies that the assigned vessel carries the whole demand; the capacity check is on the demand quantity.
- The 0 t was a display of an unused gene, not a modelled allocation.

**Fix:** decoded cargo = assigned demand quantity (0 if unassigned). The gene is kept only for vector compatibility and documented as inert. Objectives are unchanged, since cargo never entered them.

**Remaining limitation:** fuel does not depend on cargo load, because design displacement is used.

## 4. NSGA-III archive points (3.56 t and 4.27 t)

Every vessel was in `dp` or `port` mode on its assigned leg (the §2.1 loophole), which produced the 60,000 penalty (3 vessels × 4 scenarios × 5,000).
- The points were hard-feasible under the old rules but not penalty-free.
- They entered the archive because it tested only `is_feasible`.
- They were never served, but the extractor still sorted them.
- Now they are hard-infeasible (stationary mode). Both NSGA-III and Hybrid QI archives admit only `is_feasible and penalty == 0`, and feasibility is evaluated before non-dominated sorting.

## 5. Feasible search space (controlled diagnostic)

| Measure | Value |
|---|---|
| Uniform random sample over the full box | 20,000 |
| Hard-feasible | 7 (0.035 %) |
| Penalty-free | **0** |
| Rejection: incompatible fuel | 11,848 |
| Rejection: stationary mode on an assigned leg | 4,461 |
| Rejection: incompatible assignment | 3,212 |
| Rejection: capacity | 347 |
| Rejection: unfulfilled demand | 124 |
| Rejection: soft-penalised | 7 |
| Rejection: out of domain | 1 |
| Penalty-free commanded-speed window (in-band, in-domain, on time in all 4 scenarios) | Poseidon 19.25–22.0; Triton 15.75–17.5; Ceto 11.75–13.75 kn (0.25 kn grid) |
| Exhaustive grid (12 × 8 × 9 speeds × 18 fuel mixes × 8 shore-power) | 124,416 candidates, all penalty-free and distinct |
| Distinct objective vectors | 124,416 |
| **Non-dominated (fuel, cost, GHG)** | **6** |

The valid space is small and fragmented in the encoding: categorical genes are continuous, so most random vectors hit an incompatible fuel. That is why random-initialised optimizers rarely reach it. The constraints do not collapse the space: once inside it, there is a lot of freedom (124,416 valid grid plans).

## 6. Objective-conflict analysis (penalty-free grid)

| Pair | Spearman ρ |
|---|---|
| fuel vs cost | **+0.999** (aligned: cost is mostly fuel mass × price) |
| fuel vs GHG | −0.479 (conflict) |
| cost vs GHG | −0.494 (conflict) |

- **Speed:** within the valid window every objective rises with speed (ρ between +0.01 and +0.12). Delay is constrained to zero, so the slowest on-time speed dominates; speed is not a trade-off dimension here.
- **Fuel choice drives the trade-off:**
  - Poseidon: LNG dominates VLSFO (less mass, cheaper, lower WtW), so VLSFO never appears for Poseidon.
  - Triton: bio-methanol lowers GHG and raises cost.
  - Ceto: green ammonia cuts GHG sharply (mean 682 vs 767 tCO2e for VLSFO) and raises cost.
- **Shore power** adds cost and changes neither fuel nor GHG, so it is always dominated. See §9.3.

Conclusion: the objectives genuinely conflict (cost against GHG), and a multi-point front is the correct answer. One point was not expected.

## 7. Optimizer comparison (post-fix, random init, 30 seeds × 2,500 evaluations, formulation D)

| Algorithm | Final plan hard-feasible | Final plan penalty-free | Runs that ever found a penalty-free plan | Median penalty-free evaluations | Median non-dominated per run | Lowest penalty-free cost / GHG | Median runtime |
|---|---|---|---|---|---|---|---|
| Hybrid QI A5 (with repair) | 30/30 | 30/30 | 30 | 39 | 5 | $173,605 / 630.66 t | 1.81 s |
| NSGA-III (pymoo) | 22/30 | 17/30 | 17 | 664 | 3 | $173,572 / 610.42 t | 1.70 s |
| QPSO | 12/30 | 10/30 | 10 | 0 | 0 | $171,151 / 639.87 t | 0.40 s |
| DE | 24/30 | 3/30 | 3 | 0 | 0 | $190,077 / 745.21 t | 0.45 s |
| Classical GA | 8/30 | 1/30 | 1 | 0 | 0 | $254,339 / 610.67 t | 0.52 s |

Source: `results/algorithm_multiobjective_results.csv`. Invalid and penalised plans are excluded from every "penalty-free" column.

A5's lead comes from its repair operator, which maps categorical genes to compatible values; it is specific to this instance. With structured initialisation (the operator search), NSGA-III reaches 8,639–8,935 penalty-free evaluations per 10,000 and 4–6 non-dominated plans per seed (`results/pareto_search_runs.csv`).

## 8. Real bugs found and fixed

| # | Defect | Fix |
|---|---|---|
| 1 | Stationary mode completes an assigned voyage | Decoder: `port` / `dp` on an assigned leg is a hard incompatibility |
| 2 | Dead cargo gene displayed as an allocation | Decoder: carried cargo = assigned demand quantity; gene documented as inert |
| 3 | NSGA-III without selection, sorting or reference directions | `src/algorithms/nsga3.py` rewritten on pymoo 0.6 NSGA-III: 3 objectives, Das-Dennis (45 directions), constraint g = total penalty ≤ 0 |
| 4 | Archives admitted penalised plans | NSGA-III and Hybrid QI archives admit only feasible, penalty-free plans |
| 5 | Front built from scalarised run-ends | Front = non-dominated penalty-free archive of a true multi-objective search |
| 6 | Trade-off "demonstrations" were penalised DE plans (22 h delay, labelled feasible) | Selected from the verified front by explicit rules |
| 7 | `reproduce_release` reported the optimizer PASS from the pre-fix Phase 5 artifact | Step 8 now re-evaluates the post-fix front; Phase 5 is labelled PRE-FIX HISTORICAL |

No constraint was relaxed. The speed band, surrogate domain, deadlines, fuel compatibility and exactly-once assignment are unchanged; one hard constraint was added.

## 9. Correction applied, and what remains open

1. **Pareto pipeline:**
   1. candidate (NSGA-III, structured initialisation: each vessel's categorical genes individually valid, fleet rules not pre-satisfied);
   2. `Phase4FleetEvaluator` (kinematics, surrogate domain per scenario, physics, penalties);
   3. hard-feasible AND penalty-free filter;
   4. non-dominated sort on (fuel, cost, GHG);
   5. dedup;
   6. `results/pareto_front.csv` storing solution_id, seed, evaluation_index, penalty, domain_status, objectives, decisions and the full `x_vector`.

   Resolve re-evaluates the stored vector; there is no optimizer re-run.
2. **Structured initialisation** is used only for the operator Pareto search. The equal-budget benchmark keeps random initialisation for every algorithm, including NSGA-III.
3. **Open defect, not applied (it needs a modelling decision): shore power is one-sided** in both `Phase4FleetEvaluator` and `SIHObjectiveEngine`. The tariff and connection fee are charged, but berth auxiliary-engine fuel without shore power is never modelled, so shore power can only lose.
   - Proposed correction: berth fuel = hotel_load_kW × port_hours × SFOC (the evaluator already uses 0.220 kg/kWh for the hotel floor) in the vessel's fuel when shore power is off; grid emissions (configs/fuels.yaml, 450 g/kWh) when it is on.
   - Expected effect: shore power becomes a genuine cost-versus-GHG option and the front grows.
   - This changes the cost and GHG science verified by G7/G8 and the Scenario Lab, so it is left for an explicit decision.
4. **Formulation-weight insensitivity** of scalarised runs (§2.4) is a property of the penalty scale. It is documented, not changed.

## 10. Effect on Pareto diversity

The front went from 1 invalid plan to 6 valid plans (PRE shore-power correction; superseded — see top note):

| ID | Fuels (Poseidon / Triton / Ceto) | Fuel t | Cost $ | WtW tCO2e |
|---|---|---|---|---|
| PS-01 | LNG / VLSFO / VLSFO | 177.23 | 170,688.96 | 727.85 |
| PS-02 | LNG / VLSFO / bio-methanol | 202.73 | 200,347.56 | 720.36 |
| PS-03 | LNG / VLSFO / green NH3 | 206.26 | 205,554.69 | 650.59 |
| PS-04 | LNG / bio-methanol / green NH3 | 244.40 | 249,927.81 | 639.41 |
| PS-05 | bio-methanol / VLSFO / green NH3 | 368.43 | 393,600.90 | 621.40 |
| PS-06 | bio-methanol / bio-methanol / green NH3 | 406.57 | 437,974.01 | 610.22 |

- Every plan is on time with no penalty, at speeds of about 19.14 / 15.65 / 11.63 kn and without shore power.
- The fuel mixes are the same 6 as the exhaustive grid's non-dominated set. Objective values are marginally better because speed is continuous rather than on a 0.25 kn grid.
- All plans are domain status NEAR_BOUNDARY (inside the training range, outside P01–P99), not OUT_OF_DOMAIN.

## 11. Test strategy

`tests/test_pareto_contract.py`:
- stationary modes are infeasible;
- carried cargo = demand;
- NSGA-III selection improves and its archive is penalty-free;
- every stored point is feasible, penalty-free, in band, compatible, non-dominated, unique, and re-evaluates to its stored objectives.

`tests/test_api.py`:
- existing `test_pareto_is_feasible_and_deduplicated` (≥ 2 points) is unchanged;
- resolve reproduces the stored plan;
- the summary sentence states the count and never says "best".

## 12. Release-gate strategy

- **G9** keeps ≥ 2 distinct points and now also requires every point to be feasible, penalty-free and mutually non-dominated.
- **G14** scene 11 keeps its ≥ 2 check and adds the same two checks.

Nothing was weakened. The ≥ 2 requirement reflects the spec's multi-objective deliverable (min fuel, min emissions, min cost). On this instance the mathematics yields 6 points, so no gate refinement is needed. If a future instance legitimately had one non-dominated plan, the gate should then check "front equals the exhaustive or verified non-dominated set" rather than a count. That would be a documented specification change, not a relaxation.
