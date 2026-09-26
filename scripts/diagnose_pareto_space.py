"""
Scientific diagnostic of the fleet decision space (no optimisation).

A. Uniform random sample over the full decision box: how often candidates are hard-feasible and
   penalty-free, and which constraints reject them.
B. Exhaustive grid over the valid region: every compatible fuel x shore-power combination and a speed
   grid inside each vessel's penalty-free window (derived from the kinematics, the vessel speed band,
   the surrogate DomainChecker and the demand deadline under all four weather scenarios; nothing is
   hard-coded). Every candidate is evaluated by the authoritative Phase4FleetEvaluator.

Outputs results/diagnostics/pareto_space_grid.csv and results/diagnostics/pareto_space_summary.json.
"""

import itertools
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from optimization.canonical_mapper import canonicalize_vessel_type, get_baseline_fuel_for_vessel  # noqa: E402
from optimization.fleet_evaluator_phase4 import Phase4FleetEvaluator  # noqa: E402
from optimization.fleet_heterogeneous import DECISION_DIMS_PER_VESSEL, OPERATIONAL_DEMANDS, REV_DEMAND_KEYS  # noqa: E402
from optimization.variables import FUEL_MAP, REV_FUEL_MAP, REV_MODE_MAP  # noqa: E402
from run_multiobjective_tradeoffs import load_real_surrogates  # noqa: E402
from src.benchmark.metrics import is_pareto_efficient  # noqa: E402

OUT = REPO / "results" / "diagnostics"
ASSIGN = {"CPS_Poseidon": "DEMAND-A", "CPS_Triton": "DEMAND-B", "OSS_Ceto": "DEMAND-C"}
OBJ = ["fuel_tonnes", "cost_usd", "ghg_tonnes"]


def row(ev, x):
    r = ev.evaluate_vector(x)
    return {
        "x_vector": json.dumps([round(float(v), 4) for v in x]),
        "feasible": bool(r.is_feasible), "penalty": float(r.total_penalty_value),
        "pareto_feasible": bool(r.is_feasible and r.total_penalty_value <= 0.0),
        "domain_status": r.domain_status, "hard": "; ".join(r.hard_violations[:2]),
        "soft": json.dumps({k: round(v, 1) for k, v in r.soft_penalties.items()}),
        "fuel_tonnes": r.total_fuel_tonnes, "cost_usd": r.total_opex_usd, "ghg_tonnes": r.total_wtw_ghg_tonnes,
        "delay_hours": r.total_schedule_delay_hours, "risk": r.uncertainty_risk_metric,
        **{f"speed_{k}": v for k, v in r.speed_decisions.items()},
        **{f"fuel_{k}": v for k, v in r.fuel_decisions.items()},
        **{f"shore_{k}": v for k, v in r.shore_power_decisions.items()},
    }


def penalty_free_window(ev, v, step=0.25):
    dem = OPERATIONAL_DEMANDS[ASSIGN[v.vessel_id]]
    sur = ev.surrogates[v.vessel_id]
    ok = []
    for cmd in np.arange(v.min_speed_knots, v.max_speed_knots + 1e-9, step):
        good = True
        for s in ev.weather_scenarios:
            k = ev.kinematics_engine.evaluate_leg_kinematics(
                distance_nm=dem.distance_nm, commanded_speed_kn=cmd, wave_height_m=s.wave_height_m,
                wind_speed_ms=s.wind_speed_ms, operating_mode="transit", vessel_class=v.class_family)
            a = k["actual_speed_kn"]
            dom = sur.domain_checker.evaluate_point({
                "stw_kn": a, "sog_kn": a, "draft_m": v.design_draft_m, "displacement_t": v.displacement_t,
                "wind_speed_ms": s.wind_speed_ms, "wind_direction_deg": s.wind_direction_deg,
                "wave_height_m": s.wave_height_m, "wave_period_s": s.wave_period_s, "wave_direction_deg": 180.0,
                "current_speed_ms": s.current_speed_ms, "current_direction_deg": s.current_direction_deg,
                "water_depth_m": s.water_depth_m, "vessel_type": canonicalize_vessel_type(v.class_family),
                "fuel_type": get_baseline_fuel_for_vessel(v.vessel_id)})["domain_status"]
            if (dom in ("OUT_OF_DOMAIN", "PHYSICALLY_INVALID") or not v.min_speed_knots <= a <= v.max_speed_knots
                    or k["total_duration_hours"] > dem.deadline_hours):
                good = False
                break
        if good:
            ok.append(round(float(cmd), 2))
    return ok


def reason_of(r):
    h = r["hard"].split(";")[0]
    for needle, label in [("cannot complete", "stationary mode on an assigned leg"),
                          ("Duplicate demand", "duplicate demand assignment"),
                          ("unfulfilled", "unfulfilled demand"),
                          ("Incompatible fuel", "incompatible fuel"),
                          ("Incompatible assignment", "incompatible vessel-demand assignment"),
                          ("out of domain", "surrogate out of domain")]:
        if needle in h:
            return label
    return h[:60]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ev = Phase4FleetEvaluator(surrogates=load_real_surrogates())
    ev.weights = np.array([0.35, 0.35, 0.30, 0.0, 0.0])
    xl, xu = ev.get_bounds()

    # A. Uniform random sample over the full box.
    rng = np.random.default_rng(2026)
    n_rand = 20000
    rand = [row(ev, rng.uniform(xl, xu)) for _ in range(n_rand)]
    reasons = Counter()
    for r in rand:
        if not r["feasible"]:
            reasons[reason_of(r)] += 1
        elif r["penalty"] > 0:
            reasons["feasible but soft-penalised: " + ",".join(sorted(json.loads(r["soft"]).keys()))] += 1

    # B. Exhaustive grid over the valid region.
    windows = {v.vessel_id: penalty_free_window(ev, v) for v in ev.vessels}
    fuels = {v.vessel_id: [f for f in FUEL_MAP.values() if f in v.compatible_fuels] for v in ev.vessels}
    grid = []
    for sp in itertools.product(*[windows[v.vessel_id] for v in ev.vessels]):
        for fu in itertools.product(*[fuels[v.vessel_id] for v in ev.vessels]):
            for sh in itertools.product([0.0, 1.0], repeat=len(ev.vessels)):
                x = np.zeros(len(ev.vessels) * DECISION_DIMS_PER_VESSEL)
                for i, v in enumerate(ev.vessels):
                    x[i * 6: i * 6 + 6] = [REV_DEMAND_KEYS[ASSIGN[v.vessel_id]], 0.0, sp[i], REV_FUEL_MAP[fu[i]],
                                           REV_MODE_MAP["transit"], sh[i]]
                grid.append(row(ev, x))
    g = pd.DataFrame(grid)
    g.to_csv(OUT / "pareto_space_grid.csv", index=False)

    pf = g[g["pareto_feasible"]].copy()
    distinct = pf.drop_duplicates(subset=OBJ)
    nd = distinct[is_pareto_efficient(distinct[OBJ].values)]
    corr = pf[OBJ].corr(method="spearman").round(3).to_dict()

    def effect(prefix):
        return {c: pf.groupby(c)[OBJ].mean().round(2).to_dict(orient="index") for c in pf.columns if c.startswith(prefix)}

    speed_corr = {c: pf[[c] + OBJ].corr(method="spearman")[c][OBJ].round(3).to_dict() for c in pf.columns if c.startswith("speed_")}
    decision_cols = [c for c in nd.columns if c.startswith(("speed_", "fuel_CPS", "fuel_OSS", "shore_"))]

    summary = {
        "random_sample": {
            "n": n_rand,
            "hard_feasible": int(sum(r["feasible"] for r in rand)),
            "penalty_free_feasible": int(sum(r["pareto_feasible"] for r in rand)),
            "rejection_reasons": dict(reasons.most_common()),
        },
        "valid_region": {
            "speed_windows_kn": {k: [w[0], w[-1], len(w)] if w else None for k, w in windows.items()},
            "compatible_fuels_reachable": fuels,
            "grid_candidates": int(len(g)),
            "hard_feasible": int(g["feasible"].sum()),
            "penalty_free_feasible": int(g["pareto_feasible"].sum()),
            "distinct_decision_vectors": int(g["x_vector"].nunique()),
            "distinct_objective_vectors": int(len(distinct)),
            "non_dominated_fuel_cost_ghg": int(len(nd)),
            "spearman_objective_correlation": corr,
            "spearman_speed_vs_objectives": speed_corr,
            "mean_objectives_by_fuel": effect("fuel_"),
            "mean_objectives_by_shore_power": effect("shore_"),
            "non_dominated_points": nd[OBJ + decision_cols].sort_values("cost_usd").to_dict(orient="records"),
        },
    }
    (OUT / "pareto_space_summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary["valid_region"].items() if k != "non_dominated_points"}, indent=1, default=str))
    print(json.dumps(summary["random_sample"], indent=1))
    print(nd[OBJ + decision_cols].sort_values("cost_usd").to_string())


if __name__ == "__main__":
    main()
