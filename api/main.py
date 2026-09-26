"""
Egreen Quanta HTTP API — thin adapter over the authoritative Python backend.

Every scientific number returned here is computed by existing repository modules
(serving predictor, SIH objective engine, fleet evaluator/optimizers) or read from a
committed artifact, and each payload says which. No calculation is duplicated here.

Run:  .venv/Scripts/python -m uvicorn api.main:app --port 8000
"""

import copy
import dataclasses
import hashlib
import json
import math
import os
import sqlite3
import sys
import threading
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

REPO_ROOT = Path(__file__).resolve().parent.parent
for p in (REPO_ROOT, REPO_ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from common.fleet_defaults import get_default_fleet_state  # noqa: E402
from optimization.sih_objective_engine import SIHObjectiveEngine  # noqa: E402
from src.qi_prediction.serving import get_production_predictor  # noqa: E402
import demo_scenarios as demo  # noqa: E402  (verified scene inputs)
from optimization.berth_model import SFOC_KG_VLSFO_PER_KWH as BERTH_SFOC  # noqa: E402

DATA_DIR = REPO_ROOT / "data" / "processed" / "real" / "fuelcast"
MODELS_DIR = REPO_ROOT / "models"
FUELS_CONFIG = REPO_ROOT / "configs" / "fuels.yaml"
PARETO_CSV = REPO_ROOT / "results" / "pareto_front.csv"
OBJECTIVE_COLS = ["fuel_tonnes", "cost_usd", "ghg_tonnes", "delay_hours"]
MODEL_INPUT_KEYS = ("vessel_type", "draft_m", "displacement_t", "wind_speed_ms", "wave_height_m", "water_depth_m")


# --------------------------------------------------------------------------- helpers

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def jsonable(obj: Any) -> Any:
    """Convert numpy/pandas/dataclass values into strict JSON (NaN -> None)."""
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return jsonable(dataclasses.asdict(obj))
    if isinstance(obj, dict):
        return {str(k): jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [jsonable(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return jsonable(obj.tolist())
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (float, np.floating)):
        f = float(obj)
        return None if math.isnan(f) or math.isinf(f) else f
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    return obj


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def vessel_or_404(vessel_id: str) -> Dict[str, Any]:
    for v in get_default_fleet_state():
        if v["id"] == vessel_id:
            return v
    raise HTTPException(404, f"Unknown vessel '{vessel_id}'")


# --------------------------------------------------------------------------- session audit

# Append-only SQLite ledger. Rows are never updated or deleted by the API, but the file is not
# cryptographically protected: anyone with filesystem access can edit it.
AUDIT_DB = Path(os.environ.get("EQ_AUDIT_DB", REPO_ROOT / "data" / "runtime" / "hmi_audit.sqlite"))
SESSION_ID = f"S-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:6]}"
OPERATOR = "HMI operator (unauthenticated)"
AUDIT_LOCK = threading.Lock()
AUDIT_COLUMNS = ("event_id", "session_id", "timestamp", "kind", "operator", "scenario_id", "recommendation_id",
                 "vessel_id", "vessel_type", "model", "model_version", "prediction_kg_h", "ood_state", "ood_band",
                 "fallback", "fuel_scenario", "optimizer", "seed", "budget", "operator_action", "warning", "payload_json")


def _db() -> sqlite3.Connection:
    AUDIT_DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(AUDIT_DB, check_same_thread=False)
    con.execute(f"CREATE TABLE IF NOT EXISTS audit_events ({', '.join(c + ' TEXT' for c in AUDIT_COLUMNS)})")
    return con


_CON = _db()
_SEQ = [0]


def record(kind: str, **payload: Any) -> Dict[str, Any]:
    """Persist an audit event (append-only) and return it."""
    with AUDIT_LOCK:
        _SEQ[0] += 1
        event = {"event_id": f"EVT-{SESSION_ID[-6:]}-{_SEQ[0]:04d}", "session_id": SESSION_ID, "timestamp": now_iso(),
                 "kind": kind, "operator": OPERATOR, **jsonable(payload)}
        trust = event.get("trust") or {}
        row = {
            **{c: None for c in AUDIT_COLUMNS},
            **{k: event.get(k) for k in ("event_id", "session_id", "timestamp", "kind", "operator", "scenario_id",
                                         "recommendation_id", "vessel_id", "vessel_type", "model", "model_version",
                                         "fuel_scenario", "optimizer", "seed", "budget")},
            "prediction_kg_h": event.get("prediction"),
            "ood_state": trust.get("state"), "ood_band": trust.get("ood_band"),
            "fallback": trust.get("fallback_label"),
            "operator_action": event.get("decision"),
            "warning": trust.get("reason") or event.get("error"),
            "payload_json": json.dumps(event),
        }
        _CON.execute(f"INSERT INTO audit_events VALUES ({', '.join('?' for _ in AUDIT_COLUMNS)})",
                     [None if row[c] is None else str(row[c]) for c in AUDIT_COLUMNS])
        _CON.commit()
    return event


def audit_events(current_session: bool = True, limit: int = 500) -> List[Dict[str, Any]]:
    op = "=" if current_session else "!="
    with AUDIT_LOCK:
        rows = _CON.execute(f"SELECT payload_json FROM audit_events WHERE session_id {op} ? ORDER BY rowid DESC LIMIT ?",
                            (SESSION_ID, limit)).fetchall()
    return [json.loads(r[0]) for r in reversed(rows)]


# --------------------------------------------------------------------------- prediction + trust

PREDICTOR = get_production_predictor()
ENGINE = SIHObjectiveEngine()


def classify_trust(res: Dict[str, Any], point: Dict[str, Any]) -> Dict[str, Any]:
    """Map the serving router's own outcome onto operator trust states (no re-computation)."""
    route = res.get("routing_status")
    warning = res.get("warning") or ""
    source = res.get("prediction_source")
    if route == "REJECT":
        if warning.startswith("Input validation failure"):
            state = "INVALID_INPUT"
        elif warning.startswith("Physics baseline failure"):
            state = "RUNTIME_FAILURE"
        else:
            state = "OOD"
    elif route == "EMERGENCY_PHYSICS":
        state = "OOD" if not res.get("in_domain") else "RUNTIME_FAILURE"
    elif route == "FALLBACK":
        if "exception" in warning.lower():
            state = "RUNTIME_FAILURE"
        elif "near training envelope" in warning:
            state = "WARNING"
        else:
            state = "FALLBACK"
    else:
        state = "WARNING" if (res.get("uncertainty") or {}).get("is_high_uncertainty") else "NORMAL"

    guard = PREDICTOR.config.get("domain_guard", {})
    thresholds = {
        "warning": guard.get("envelope_distance_threshold_warning", 1.0),
        "ood": guard.get("envelope_distance_threshold_ood", 1.5),
        "reject": guard.get("envelope_distance_threshold_critical", 3.0),
    }
    dist = res.get("envelope_distance")
    if dist is None or state == "INVALID_INPUT":
        band = "NOT_EVALUATED"
    elif warning.startswith("Unsupported vessel_type"):
        band = "CATEGORICAL"  # outside the trained vessel categories; numeric distance does not apply
    elif dist > thresholds["reject"]:
        band = "REJECT"
    elif dist > thresholds["ood"]:
        band = "OOD"
    elif dist > thresholds["warning"]:
        band = "NEAR_BOUNDARY"
    else:
        band = "IN_DOMAIN"

    fallback_label = None
    if route in ("FALLBACK", "EMERGENCY_PHYSICS"):
        fallback_label = "MODEL-REAL-04 FALLBACK" if source == "MODEL_REAL_04" else "PHYSICS EMERGENCY FALLBACK — NOT A RECOMMENDATION"

    missing = [f for f in PREDICTOR.all_features if point.get(f) is None]
    return {
        "state": state,
        "fallback": fallback_label is not None,
        "fallback_label": fallback_label,
        "ood_band": band,
        "envelope_distance": dist,
        "thresholds": thresholds,
        "reason": warning or None,
        "missing_factors": missing,
        "input_completeness_pct": round(100.0 * (1 - len(missing) / len(PREDICTOR.all_features)), 1),
        "missing_factor_note": "Missing optional factors are filled with serving-contract defaults.",
    }


def predict_point(point: Dict[str, Any], coverage: float = 0.90) -> Dict[str, Any]:
    try:
        res = PREDICTOR.predict_fuel_with_uncertainty(point, coverage=coverage, raise_on_error=False)
    except Exception as exc:  # surfaced as an explicit RUNTIME_FAILURE, never a number
        res = {"fuel_prediction": None, "routing_status": "REJECT", "prediction_source": "REJECT",
               "confidence": "LOW", "uncertainty": None, "model": "None",
               "warning": f"Physics baseline failure: {type(exc).__name__}: {exc}", "timestamp": now_iso()}
    return {"input": jsonable(point), "result": jsonable(res), "trust": classify_trust(res, point)}


def vessel_point(v: Dict[str, Any], speed_kn: Optional[float] = None) -> Dict[str, Any]:
    speed = float(speed_kn if speed_kn is not None else v["stw_kn"])
    point = {k: v[k] for k in MODEL_INPUT_KEYS}
    point.update(vessel_id=v["id"], fuel_type="vlsfo", stw_kn=speed,
                 sog_kn=float(v["sog_kn"]) if speed_kn is None else speed)
    return point


def hourly_economics(v: Dict[str, Any], rate_kg_h: float, speed_kn: float) -> Dict[str, Any]:
    """One operating hour through the SIH engine at the configured prices (scenario basis)."""
    ev = ENGINE.evaluate_voyage(vessel_id=v["id"], vessel_type=v["vessel_type"], speed_knots=speed_kn,
                                voyage_distance_nm=speed_kn, schedule_deadline_hours=1.0,
                                baseline_fuel_rate_kg_h=rate_kg_h, fuel_type="vlsfo")
    return {"cost_usd_per_h": ev.operational_cost_usd, "wtw_tco2e_per_h": ev.lifecycle_ghg_tonnes,
            "basis": "SCENARIO ESTIMATE — 1 h at configured VLSFO price and carbon price"}


# --------------------------------------------------------------------------- dataset replay

@lru_cache(maxsize=8)
def dataset(vessel_id: str) -> pd.DataFrame:
    path = DATA_DIR / f"{vessel_id}.parquet"
    if not path.exists():
        raise HTTPException(404, f"No dataset for {vessel_id}")
    return pd.read_parquet(path)


@lru_cache(maxsize=8)
def replay_trend(vessel_id: str, points: int = 120, window: int = 1440) -> Dict[str, Any]:
    """Observed vs served prediction over the last `window` records of the recorded FuelCast data."""
    df = dataset(vessel_id).tail(window)
    df = df.iloc[:: max(1, len(df) // points)]
    rows = []
    for _, r in df.iterrows():
        point = {k: (None if pd.isna(r.get(k)) else r.get(k)) for k in PREDICTOR.all_features}
        res = PREDICTOR.predict_fuel_with_uncertainty(point, raise_on_error=False)
        unc = res.get("uncertainty") or {}
        rows.append({"timestamp": r["timestamp"], "stw_kn": r.get("stw_kn"),
                     "observed_kg_h": r.get("fuel_mass_flow_kg_h"), "predicted_kg_h": res.get("fuel_prediction"),
                     "lower_kg_h": unc.get("lower_bound_kg_h"), "upper_kg_h": unc.get("upper_bound_kg_h"),
                     "source": res.get("prediction_source"), "routing": res.get("routing_status")})
    return jsonable({"provenance": "DATASET REPLAY — recorded FuelCast telemetry, not a live feed",
                     "window_records": len(dataset(vessel_id).tail(window)), "points": rows})


def latest_record(vessel_id: str) -> Dict[str, Any]:
    r = dataset(vessel_id).iloc[-1]
    return jsonable({"timestamp": r["timestamp"],
                     "inputs": {k: (None if pd.isna(r.get(k)) else r.get(k)) for k in PREDICTOR.all_features},
                     "observed_fuel_kg_h": r.get("fuel_mass_flow_kg_h"),
                     "provenance": "MEASURED — last record of the recorded FuelCast dataset (historical)"})


# --------------------------------------------------------------------------- fleet evaluator / optimizer

EVALUATOR: Dict[str, Any] = {"ready": False, "error": None, "value": None}
OPT_LOCK = threading.Lock()  # ponytail: one optimizer run at a time; add a worker pool if concurrent users matter
JOBS: Dict[str, Dict[str, Any]] = {}


def _build_evaluator() -> None:
    try:
        from experiments.exp_phase3_master_runner import load_real_surrogates
        from optimization.fleet_evaluator_phase4 import Phase4FleetEvaluator
        EVALUATOR["value"] = Phase4FleetEvaluator(surrogates=load_real_surrogates())
        EVALUATOR["ready"] = True
    except Exception as exc:
        EVALUATOR["error"] = f"{type(exc).__name__}: {exc}"


def optimizer_classes():
    from src.algorithms.de import DEOptimizer
    from src.algorithms.ga import GeneticAlgorithmOptimizer
    from src.algorithms.nsga3 import NSGA3Optimizer
    from src.algorithms.qpso import PlainQPSOOptimizer
    from src.algorithms.hybrid_qi import A5CompleteHybridQIOptimizer
    return {
        "Hybrid_QI_A5": lambda seed, gens: A5CompleteHybridQIOptimizer(seed=seed, n_particles=50, max_iterations=gens),
        "DE": lambda seed, gens: DEOptimizer(seed=seed, population_size=50, max_generations=gens),
        "Classical_GA": lambda seed, gens: GeneticAlgorithmOptimizer(seed=seed, population_size=50, max_generations=gens),
        "NSGA_III": lambda seed, gens: NSGA3Optimizer(seed=seed, population_size=50, max_generations=gens),
        "QPSO": lambda seed, gens: PlainQPSOOptimizer(seed=seed, n_particles=50, max_iterations=gens),
    }


def run_optimizer(algorithm: str, seed: int, budget: int, weights: List[float], job: Optional[Dict] = None):
    from src.evaluator.common_evaluator import CommonFleetEvaluator
    if not EVALUATOR["ready"]:
        raise HTTPException(503, EVALUATOR["error"] or "Fleet evaluator is still loading surrogates (~30 s).")
    evaluator = copy.deepcopy(EVALUATOR["value"])
    evaluator.weights = np.asarray(weights, dtype=float)
    xl, xu = evaluator.get_bounds()
    comm = CommonFleetEvaluator(evaluator, max_budget=budget)
    if job is not None:
        job["counter"] = comm
    res = optimizer_classes()[algorithm](seed, max(1, budget // 50)).optimize(comm, xl=xl, xu=xu, budget=budget)
    return solution_payload(res.best_output, res)


def solution_payload(out, res) -> Dict[str, Any]:
    if out is None:
        return {"feasible": False, "objectives": None, "vessels": [], "hard_violations": ["No solution returned"]}
    cargo = getattr(out.raw_result, "cargo_allocations", {}) or {}
    # The evaluator's hard-violation fast path returns a fixed placeholder objective vector without
    # simulating the fleet; it is not a model output, so no objectives are reported for it.
    simulated = bool(getattr(out.raw_result, "scenario_details", None))
    vessels = [{
        "vessel_id": vid,
        "assigned_demand": out.assigned_demands.get(vid),
        "cargo_tonnes": cargo.get(vid),
        "speed_kn": speed,
        "fuel": out.fuel_decisions.get(vid),
        "shore_power": out.shore_decisions.get(vid),
    } for vid, speed in out.speed_decisions.items()]
    return jsonable({
        "feasible": bool(res.feasible_at_end and out.is_feasible),
        "penalty_free": bool(out.is_feasible and out.penalty <= 0.0),
        "penalty": out.penalty,
        "soft_penalties": dict(getattr(out.raw_result, "soft_penalties", {}) or {}),
        "objectives": {"fuel_t": out.fuel_tonnes, "opex_usd": out.opex_usd, "wtw_tco2e": out.ghg_tonnes,
                       "delay_h": out.delay_hours, "risk_cvar_excess": out.risk_metric} if simulated else None,
        "penalized_fitness": out.fitness,
        "hard_violations": list(out.hard_violations),
        "vessels": vessels,
        "evaluations": res.objective_evaluations,
        "runtime_s": res.runtime_seconds,
    })


def _job_worker(job_id: str) -> None:
    job = JOBS[job_id]
    try:
        while not EVALUATOR["ready"] and not EVALUATOR["error"]:
            job["status"] = "WARMING_EVALUATOR"
            time.sleep(0.5)
        with OPT_LOCK:
            job["status"] = "RUNNING"
            job["started_at"] = now_iso()
            p = job["params"]
            job["result"] = run_optimizer(p["algorithm"], p["seed"], p["budget"], p["weights"], job)
        job["status"] = "DONE"
        job["recommendation_status"] = "PENDING_REVIEW" if job["result"]["feasible"] else "NOT_RECOMMENDABLE"
        record("OPTIMIZATION", recommendation_id=job_id, optimizer=p["algorithm"], seed=p["seed"],
               budget=p["budget"], weights=p["weights"], objectives=job["result"]["objectives"],
               selected_solution=job["result"]["vessels"], feasible=job["result"]["feasible"],
               hard_violations=job["result"]["hard_violations"], recommendation_status=job["recommendation_status"])
    except HTTPException as exc:
        job.update(status="ERROR", error=exc.detail)
    except Exception as exc:
        job.update(status="ERROR", error=f"{type(exc).__name__}: {exc}")
        record("RUNTIME_FAILURE", source="optimizer", error=job["error"], recommendation_id=job_id)
    finally:
        job["finished_at"] = now_iso()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    threading.Thread(target=_build_evaluator, daemon=True).start()
    yield


app = FastAPI(title="Egreen Quanta API", version="1.0.0", lifespan=lifespan)


# --------------------------------------------------------------------------- request models

class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    vessel_id: Optional[str] = None
    vessel_type: Optional[str] = None
    fuel_type: Optional[str] = None
    stw_kn: Optional[float] = None
    sog_kn: Optional[float] = None
    draft_m: Optional[float] = None
    displacement_t: Optional[float] = None
    wind_speed_ms: Optional[float] = None
    wind_direction_deg: Optional[float] = None
    wave_height_m: Optional[float] = None
    wave_period_s: Optional[float] = None
    wave_direction_deg: Optional[float] = None
    current_speed_ms: Optional[float] = None
    current_direction_deg: Optional[float] = None
    water_depth_m: Optional[float] = None
    coverage: Literal[0.9, 0.95] = 0.9


class ScenarioRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    vessel_id: str
    base: Literal["fleet_default", "dataset_latest"] = "fleet_default"
    overrides: Dict[str, float] = Field(default_factory=dict)
    fuel_type: str = "vlsfo"
    use_shore_power: bool = False
    port_hours: float = Field(0.0, ge=0, le=240)
    distance_nm: float = Field(300.0, gt=0, le=20000)
    deadline_h: float = Field(24.0, gt=0, le=2000)


class OptimizeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    algorithm: Literal["Hybrid_QI_A5", "DE", "Classical_GA", "NSGA_III", "QPSO"] = "Hybrid_QI_A5"
    seed: int = Field(1005, ge=1, le=99999)
    budget: Literal[1000, 2500, 5000, 10000] = 2500
    weights: List[float] = Field(default_factory=lambda: [0.35, 0.35, 0.30, 0.0, 0.0], min_length=5, max_length=5)


class DecisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    decision: Literal["ACCEPT", "REJECT"]
    note: str = Field("", max_length=500)


# --------------------------------------------------------------------------- routes: status / fleet / vessel

def model_registry() -> Dict[str, Any]:
    metas = {}
    for f in ("qi_c1_vessel_type_meta.json", "qi_c1_meta.json", "model_real_04_meta.json"):
        m = json.loads((MODELS_DIR / f).read_text(encoding="utf-8"))
        metas[m.get("model_id", f)] = {"version": m.get("version"), "features": m.get("features"),
                                        "reference_test_mae_kg_h": m.get("test_mae_kg_h"),
                                        "reference_test_r2": m.get("test_r2")}
    return {"primary": "QI-C1-vessel-type", "reference_anchor": "MODEL-REAL-04",
            "serving_version": "1.0.0-production", "models": metas,
            "note": "Reference metrics are from models/*_meta.json (frozen evaluation)."}


@app.get("/api/status")
def status() -> Dict[str, Any]:
    fleet = get_default_fleet_state()
    session = audit_events()
    last_rec = next((e for e in reversed(session) if e["kind"] in ("OPTIMIZATION", "OPERATOR_DECISION")), None)
    last_pred = next((e for e in reversed(session) if "trust" in e), None)
    return {
        "server_time": now_iso(),
        "data_mode": "SIMULATION",
        "live_feed_connected": False,
        "data_freshness": {v["id"]: str(dataset(v["id"])["timestamp"].iloc[-1]) for v in fleet},
        "data_freshness_note": "No live telemetry feed. Vessel states are fleet defaults; trends replay recorded FuelCast data.",
        "fleet_count": len(fleet),
        "model": model_registry(),
        "evaluator_ready": EVALUATOR["ready"],
        "evaluator_error": EVALUATOR["error"],
        "session_events": len(session),
        "fleet_trust": [{"vessel_id": v["id"], **{k: t[k] for k in ("state", "fallback", "fallback_label", "ood_band")}}
                        for v in fleet for t in [predict_point(vessel_point(v))["trust"]]],
        "last_recommendation": last_rec,
        "last_trust": last_pred["trust"] if last_pred else None,
    }


@app.get("/api/fleet")
def fleet() -> Dict[str, Any]:
    rows = []
    for v in get_default_fleet_state():
        pred = predict_point(vessel_point(v))
        rate = pred["result"].get("fuel_prediction")
        rows.append({
            "vessel": jsonable(v),
            "provenance": "ASSUMED — fleet default operating state (common/fleet_defaults.py)",
            "prediction": pred,
            "economics": hourly_economics(v, rate, v["stw_kn"]) if rate is not None else None,
            "schedule": None,
            "schedule_note": "No voyage-schedule feed is connected; schedule status is not tracked.",
        })
    served = [r for r in rows if r["prediction"]["result"].get("fuel_prediction") is not None]
    kpis = {
        "vessels": len(rows),
        "vessels_with_prediction": len(served),
        "predicted_fuel_kg_h": sum(r["prediction"]["result"]["fuel_prediction"] for r in served),
        "cost_usd_per_h": sum(r["economics"]["cost_usd_per_h"] for r in served),
        "wtw_tco2e_per_h": sum(r["economics"]["wtw_tco2e_per_h"] for r in served),
        "non_normal": sum(r["prediction"]["trust"]["state"] != "NORMAL" for r in rows),
    }
    return {"generated_at": now_iso(), "kpis": kpis, "vessels": rows}


@app.get("/api/vessels/{vessel_id}")
def vessel_detail(vessel_id: str) -> Dict[str, Any]:
    v = vessel_or_404(vessel_id)
    return {"vessel": jsonable(v), "prediction": predict_point(vessel_point(v)),
            "latest_record": latest_record(vessel_id), "trend": replay_trend(vessel_id),
            "model_features": {"QI-C1-vessel-type": PREDICTOR.qi_vt_features,
                               "MODEL-REAL-04": PREDICTOR.all_features},
            "physical_bounds": PREDICTOR.physical_bounds}


@app.post("/api/predict")
def predict(req: PredictRequest) -> Dict[str, Any]:
    point = req.model_dump(exclude={"coverage"}, exclude_none=True)
    out = predict_point(point, coverage=req.coverage)
    record("PREDICTION", vessel_id=point.get("vessel_id"), vessel_type=point.get("vessel_type"), inputs=point,
           model=out["result"].get("model"), model_version=out["result"].get("model_version"),
           prediction=out["result"].get("fuel_prediction"), uncertainty=out["result"].get("uncertainty"),
           trust=out["trust"])
    return out


# --------------------------------------------------------------------------- routes: scenario / fuels

def fuel_assumptions(fuel: str) -> Dict[str, Any]:
    p = ENGINE.registry.get_pathway(fuel)
    keys = ("name", "lhv_mj_kg", "wtt_ghg_g_co2e_mj", "ttw_co2_g_per_g_fuel", "ttw_ch4_g_per_g_fuel",
            "ttw_n2o_g_per_g_fuel", "methane_slip_fraction", "source", "confidence")
    return {**{k: p.get(k) for k in keys}, "price_usd_per_tonne": ENGINE.bunker_prices[fuel]}


def config_meta() -> Dict[str, Any]:
    return {"fuels_config": rel(FUELS_CONFIG), "fuels_config_sha256": sha256(FUELS_CONFIG),
            "carbon_price_usd_per_tco2": ENGINE.cost_engine.carbon_price_usd_tonne,
            "demurrage_usd_per_h": ENGINE.cost_engine.demurrage_rate_usd_hour,
            "shore_power_tariff_usd_per_kwh": ENGINE.shore_power_tariff,
            "shore_power_connection_fee_usd": ENGINE.shore_power_connect_fee,
            "shore_power_grid_factor_g_co2e_per_kwh": ENGINE.shore_power_grid_emission_factor,
            "berth_sfoc_kg_per_kwh": BERTH_SFOC, "berth_sfoc_provenance": "ASSUMED (optimization/berth_model.py)"}


def voyage(v: Dict[str, Any], rate: float, speed: float, fuel: str, shore: bool, port_h: float,
           distance: float, deadline: float) -> Dict[str, Any]:
    ev = ENGINE.evaluate_voyage(vessel_id=v["id"], vessel_type=v["vessel_type"], speed_knots=speed,
                                voyage_distance_nm=distance, schedule_deadline_hours=deadline,
                                baseline_fuel_rate_kg_h=rate, fuel_type=fuel, use_shore_power=shore,
                                port_hours=port_h, hotel_load_kw=v["hotel_load_kw"])
    hours = distance / speed
    return jsonable({"fuel_type": ev.fuel_type, "voyage_hours": hours, "fuel_t": ev.fuel_tonnes,
                     "fuel_rate_kg_h": (ev.fuel_tonnes - ev.berth_fuel_tonnes) * 1000.0 / hours,  # sea passage only
                     "berth": {"source": ev.berth_source, "hours": port_h, "hotel_load_kw": v["hotel_load_kw"],
                               "energy_kwh": ev.berth_energy_kwh, "fuel_t": ev.berth_fuel_tonnes,
                               "cost_usd": ev.berth_cost_usd, "ghg_tco2e": ev.berth_ghg_tonnes},
                     "cost": {"total_usd": ev.operational_cost_usd, "fuel_usd": ev.fuel_cost_usd,
                              "carbon_usd": ev.carbon_cost_usd, "shore_power_usd": ev.shore_power_cost_usd,
                              "schedule_penalty_usd": ev.schedule_penalty_usd, "fueleu_penalty_usd": ev.fueleu_penalty_usd},
                     "ghg": {"wtw_tco2e": ev.lifecycle_ghg_tonnes, "wtt_tco2e": ev.wtt_ghg_tonnes,
                             "ttw_tco2e": ev.ttw_ghg_tonnes, "methane_slip_tco2e": ev.methane_slip_tonnes},
                     "schedule": {"delay_h": ev.schedule_delay_hours, "deadline_h": deadline},
                     "feasible": ev.is_feasible})


@app.post("/api/scenario")
def scenario(req: ScenarioRequest) -> Dict[str, Any]:
    v = vessel_or_404(req.vessel_id)
    if req.fuel_type not in ENGINE.registry.pathways:
        raise HTTPException(422, f"Unsupported fuel_type '{req.fuel_type}'. Supported: {sorted(ENGINE.registry.pathways)}")
    allowed = {"stw_kn", "draft_m", "displacement_t", "wind_speed_ms", "wave_height_m", "wave_period_s", "water_depth_m"}
    bad = set(req.overrides) - allowed
    if bad:
        raise HTTPException(422, f"Unsupported override(s): {sorted(bad)}")

    if req.base == "dataset_latest":
        lr = latest_record(req.vessel_id)
        point = {k: val for k, val in lr["inputs"].items() if val is not None}
        base_label = f"MEASURED (historical record {lr['timestamp']})"
    else:
        point = vessel_point(v)
        base_label = "ASSUMED (fleet default)"
    point.update(vessel_id=v["id"], vessel_type=v["vessel_type"], fuel_type="vlsfo")
    for k, val in req.overrides.items():
        point[k] = val
        if k == "stw_kn":
            point["sog_kn"] = val
    overridden = set(req.overrides) | ({"sog_kn"} if "stw_kn" in req.overrides else set())
    provenance = {k: ("SCENARIO INPUT" if k in overridden else base_label) for k in point}
    for k in ("fuel_type_scenario", "use_shore_power", "port_hours", "distance_nm", "deadline_h"):
        provenance[k] = "SCENARIO INPUT"

    pred = predict_point(point)
    rate = pred["result"].get("fuel_prediction")
    result = None
    if rate is not None:
        result = voyage(v, rate, float(point["stw_kn"]), req.fuel_type, req.use_shore_power, req.port_hours,
                        req.distance_nm, req.deadline_h)
    out = {"prediction": pred, "voyage": result, "provenance": provenance,
           "basis": ("VLSFO rate from the prediction model at the scenario state; other fuels converted on an "
                     "equal-energy LHV basis by the SIH engine. SCENARIO ESTIMATE, not measured telemetry."),
           "unsupported_inputs": ["cargo — cargo allocation is modelled only by the Fleet Optimizer"],
           "assumptions": {"fuel": fuel_assumptions(req.fuel_type), **config_meta(),
                           "hotel_load_kw": v["hotel_load_kw"], "hotel_load_provenance": "ASSUMED (fleet default)"}}
    scen_id = f"SCEN-{req.vessel_id}-{uuid.uuid4().hex[:6]}"
    out["scenario_id"] = scen_id
    record("SCENARIO", scenario_id=scen_id, vessel_id=v["id"], vessel_type=v["vessel_type"], inputs=point,
           fuel_scenario=req.fuel_type, prediction=rate, trust=pred["trust"], voyage=result,
           fuel_price_config=out["assumptions"]["fuel"]["price_usd_per_tonne"],
           lifecycle_config_sha256=out["assumptions"]["fuels_config_sha256"])
    return out


@app.get("/api/fuels")
def fuels(vessel_id: str = "CPS_Poseidon", speed_kn: float = 14.5, distance_nm: float = 250.0,
          port_hours: float = 6.0) -> Dict[str, Any]:
    v = vessel_or_404(vessel_id)
    if not (0 < speed_kn <= 35 and 0 < distance_nm <= 20000 and 0 <= port_hours <= 240):
        raise HTTPException(422, "speed_kn, distance_nm or port_hours out of range")
    pred = predict_point(vessel_point(v, speed_kn))
    rate = pred["result"].get("fuel_prediction")
    rows = []
    if rate is not None:
        deadline = distance_nm / speed_kn
        variants = [(f, False) for f in ENGINE.registry.pathways] + [("vlsfo", True)]
        for fuel, shore in variants:
            r = voyage(v, rate, speed_kn, fuel, shore, port_hours, distance_nm, deadline)
            label = fuel_assumptions(fuel)["name"] + (" + Shore Power at berth" if shore else "")
            r["energy_mj_h"] = r["fuel_rate_kg_h"] * fuel_assumptions(fuel)["lhv_mj_kg"]
            rows.append({"key": fuel + ("+shore" if shore else ""), "label": label, "fuel": fuel, "shore_power": shore,
                         "basis": "MODEL PREDICTION" if (fuel == "vlsfo" and not shore) else "SCENARIO ESTIMATE",
                         "measured_telemetry": False, "result": r, "assumptions": fuel_assumptions(fuel)})
    return {"vessel_id": vessel_id, "speed_kn": speed_kn, "distance_nm": distance_nm, "port_hours": port_hours,
            "prediction": pred, "rows": rows, "shore_comparison": shore_comparison(v, rate, speed_kn, port_hours, distance_nm),
            "config": {**config_meta(), "hotel_load_kw": v["hotel_load_kw"]}}


def shore_comparison(v: Dict[str, Any], rate: Optional[float], speed_kn: float, port_hours: float,
                     distance_nm: float) -> List[Dict[str, Any]]:
    """Per pathway: berth on shore power minus berth on onboard generation (same voyage, SIH engine)."""
    if rate is None or port_hours <= 0:
        return []
    out, deadline = [], distance_nm / speed_kn
    for fuel in ENGINE.registry.pathways:
        on = voyage(v, rate, speed_kn, fuel, True, port_hours, distance_nm, deadline)
        off = voyage(v, rate, speed_kn, fuel, False, port_hours, distance_nm, deadline)
        d_cost = on["cost"]["total_usd"] - off["cost"]["total_usd"]
        d_ghg = on["ghg"]["wtw_tco2e"] - off["ghg"]["wtw_tco2e"]
        out.append({"fuel": fuel, "label": fuel_assumptions(fuel)["name"],
                    "onboard_berth": off["berth"], "shore_berth": on["berth"],
                    "delta_cost_usd": round(d_cost, 2), "delta_wtw_tco2e": round(d_ghg, 4),
                    "ghg_effect": "REDUCES GHG" if d_ghg < 0 else "INCREASES GHG" if d_ghg > 0 else "NO GHG CHANGE",
                    "cost_effect": "CHEAPER" if d_cost < 0 else "MORE EXPENSIVE" if d_cost > 0 else "SAME COST",
                    "basis": "SCENARIO ESTIMATE"})
    return out


# --------------------------------------------------------------------------- routes: optimizer / pareto / decisions

@app.get("/api/optimizer/config")
def optimizer_config() -> Dict[str, Any]:
    from optimization.fleet_evaluator_phase4 import Phase4FleetEvaluator
    from optimization.fleet_heterogeneous import FLEET_VESSELS, OPERATIONAL_DEMANDS, WEATHER_SCENARIOS
    from run_multiobjective_tradeoffs import FORMULATIONS
    return jsonable({
        "evaluator_ready": EVALUATOR["ready"], "evaluator_error": EVALUATOR["error"],
        "algorithms": list(optimizer_classes()), "budgets": [1000, 2500, 5000, 10000],
        "objective_names": ["Fuel (t)", "OPEX (USD)", "WtW GHG (tCO2e)", "Schedule delay (h)", "CVaR excess (normalised loss)"],
        "formulations": FORMULATIONS,
        "decision_variables_per_vessel": ["assigned demand", "cargo (t)", "speed (kn)", "fuel pathway",
                                          "operating mode", "shore power"],
        "vessels": list(FLEET_VESSELS.values()), "demands": list(OPERATIONAL_DEMANDS.values()),
        "weather_scenarios": WEATHER_SCENARIOS,
        "constraints_doc": Phase4FleetEvaluator.__doc__,
    })


@app.post("/api/optimize")
def optimize(req: OptimizeRequest) -> Dict[str, Any]:
    if any(w < 0 for w in req.weights) or sum(req.weights) <= 0:
        raise HTTPException(422, "Weights must be non-negative with a positive sum")
    if any(j["status"] in ("QUEUED", "WARMING_EVALUATOR", "RUNNING") for j in JOBS.values()):
        raise HTTPException(409, "An optimization is already running")
    job_id = f"OPT-{uuid.uuid4().hex[:8]}"
    JOBS[job_id] = {"job_id": job_id, "status": "QUEUED", "params": req.model_dump(), "created_at": now_iso(),
                    "result": None, "error": None, "counter": None, "recommendation_status": None}
    threading.Thread(target=_job_worker, args=(job_id,), daemon=True).start()
    return job_view(job_id)


def job_view(job_id: str) -> Dict[str, Any]:
    job = JOBS.get(job_id)
    if job is None:
        raise HTTPException(404, f"Unknown job '{job_id}'")
    counter = job.get("counter")
    return jsonable({k: v for k, v in job.items() if k != "counter"} | {
        "evaluations": counter.evaluation_count if counter else 0,
        "feasible_evaluations": counter.feasible_evaluations_count if counter else 0,
        "budget": job["params"]["budget"],
        "advisory": "ADVISORY — REQUIRES HUMAN ACCEPTANCE",
    })


@app.get("/api/optimize/{job_id}")
def optimize_status(job_id: str) -> Dict[str, Any]:
    return job_view(job_id)


@app.post("/api/recommendations/{job_id}/decision")
def decide(job_id: str, req: DecisionRequest) -> Dict[str, Any]:
    job = JOBS.get(job_id)
    if job is None:
        raise HTTPException(404, f"Unknown recommendation '{job_id}'")
    if job.get("recommendation_status") != "PENDING_REVIEW":
        raise HTTPException(409, f"Recommendation is {job.get('recommendation_status')}, not PENDING_REVIEW")
    job["recommendation_status"] = "ACCEPTED" if req.decision == "ACCEPT" else "REJECTED"
    record("OPERATOR_DECISION", recommendation_id=job_id, decision=job["recommendation_status"], note=req.note,
           selected_solution=job["result"]["vessels"], objectives=job["result"]["objectives"],
           actuation="NONE — advisory only; no vessel or engine commands are issued")
    return job_view(job_id)


def pareto_points() -> List[Dict[str, Any]]:
    """Stored front rows that are hard-feasible and penalty-free; the artifact already holds only such rows."""
    df = pd.read_csv(PARETO_CSV)
    df = df[(df["is_feasible"].astype(str).str.lower() == "true") & (df["penalty"] <= 0.0)]
    df = df.drop_duplicates(subset=OBJECTIVE_COLS).reset_index(drop=True)
    return jsonable(df.to_dict(orient="records"))


PARETO_NOTE = ("Hard-feasible, penalty-free plans (on time, actual speed inside each vessel band, inside the model "
               "domain) from a multi-objective NSGA-III search, non-dominated in fuel, operational cost and WtW GHG; "
               "duplicate objective vectors removed. No point is ranked 'best': no single decision criterion is defined.")


@app.get("/api/pareto")
def pareto() -> Dict[str, Any]:
    raw = pd.read_csv(PARETO_CSV)
    pts = pareto_points()
    summary = ("One non-dominated feasible solution identified under the current constraints." if len(pts) == 1
               else f"{len(pts)} non-dominated feasible solutions identified under the current constraints.")
    return {"source": rel(PARETO_CSV), "provenance": "STORED OPTIMIZER OUTPUT (repository artifact)",
            "archived_rows": len(raw), "points": pts, "summary": summary, "note": PARETO_NOTE}


@app.post("/api/pareto/{solution_id}/resolve")
def resolve_pareto(solution_id: str) -> Dict[str, Any]:
    """Re-evaluate the stored decision vector with the live evaluator (deterministic; no optimizer re-run)."""
    from types import SimpleNamespace
    from run_multiobjective_tradeoffs import FORMULATIONS
    from src.evaluator.common_evaluator import CommonFleetEvaluator
    pt = next((p for p in pareto_points() if p["solution_id"] == solution_id), None)
    if pt is None:
        raise HTTPException(404, f"Unknown solution '{solution_id}'")
    if not EVALUATOR["ready"]:
        raise HTTPException(503, EVALUATOR["error"] or "Fleet evaluator is still loading surrogates (~30 s).")
    evaluator = copy.deepcopy(EVALUATOR["value"])
    evaluator.weights = np.asarray(FORMULATIONS["D_Fuel_Cost_GHG"], dtype=float)
    out = CommonFleetEvaluator(evaluator, max_budget=1).evaluate(np.asarray(json.loads(pt["x_vector"]), dtype=float))
    sol = solution_payload(out, SimpleNamespace(feasible_at_end=out.is_feasible, objective_evaluations=1, runtime_seconds=0.0))
    o = sol["objectives"]
    match = (out.is_feasible and out.penalty <= 0.0 and all(abs(a - b) <= 0.01 for a, b in (
        (o["fuel_t"], pt["fuel_tonnes"]), (o["opex_usd"], pt["cost_usd"]),
        (o["wtw_tco2e"], pt["ghg_tonnes"]), (o["delay_h"], pt["delay_hours"]))))
    return {"solution": pt, "rerun": sol, "reproduced": match,
            "note": ("Decision variables are the stored decision vector, re-evaluated by the live fleet evaluator. "
                     "'reproduced' is true only if it is still feasible and penalty-free and all four objectives "
                     "match the stored values within 0.01.")}


# --------------------------------------------------------------------------- routes: alerts / audit

@app.get("/api/alerts")
def alerts() -> Dict[str, Any]:
    items = []
    for row in fleet()["vessels"]:
        t = row["prediction"]["trust"]
        base = {"timestamp": row["prediction"]["result"].get("timestamp"), "vessel_id": row["vessel"]["id"],
                "source": "current fleet evaluation"}
        if t["state"] != "NORMAL":
            items.append({**base, "state": t["state"], "reason": t["reason"]})
        if t["fallback"]:
            items.append({**base, "state": "FALLBACK", "reason": t["fallback_label"]})
        if t["missing_factors"]:
            items.append({**base, "state": "MISSING_FACTOR", "reason": ", ".join(t["missing_factors"])})
    for e in audit_events(limit=200):
        t = e.get("trust")
        if t and t["state"] != "NORMAL":
            items.append({"timestamp": e["timestamp"], "vessel_id": e.get("vessel_id"), "state": t["state"],
                          "reason": t["reason"], "source": f"session {e['kind'].lower()} {e['event_id']}"})
        if t and t["fallback"]:
            items.append({"timestamp": e["timestamp"], "vessel_id": e.get("vessel_id"), "state": "FALLBACK",
                          "reason": t["fallback_label"], "source": f"session {e['kind'].lower()} {e['event_id']}"})
        if e["kind"] == "OPTIMIZATION" and e.get("hard_violations"):
            items.append({"timestamp": e["timestamp"], "vessel_id": None, "state": "CONSTRAINT_FAILURE",
                          "reason": "; ".join(e["hard_violations"]), "source": f"session optimization {e['event_id']}"})
        if e["kind"] == "RUNTIME_FAILURE":
            items.append({"timestamp": e["timestamp"], "vessel_id": None, "state": "RUNTIME_FAILURE",
                          "reason": e.get("error"), "source": e.get("source")})
    return {"generated_at": now_iso(), "alerts": items}


@app.get("/api/audit")
def audit() -> Dict[str, Any]:
    def load(p: Path):
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
    gate = load(REPO_ROOT / "RELEASE" / "release_gate.json")
    repro = load(REPO_ROOT / "RELEASE" / "reproduction_summary.json")
    claims = load(REPO_ROOT / "RELEASE" / "FINAL_CLAIMS.json")
    historical = {
        "label": "HISTORICAL EVIDENCE — committed repository artifacts",
        "release_gate": None if gate is None else {
            "timestamp_utc": gate.get("timestamp_utc"), "classification": gate.get("release_classification"),
            "gates_passed": gate.get("gates_passed"), "gates_evaluated": gate.get("gates_evaluated"),
            "gates": [{"id": k, "name": g.get("name"), "status": g.get("status"), "evidence": g.get("evidence")}
                      for k, g in gate.get("gates", {}).items()]},
        "reproduction": repro,
        "claims": None if claims is None else {"prohibited": claims.get("prohibited_claims"),
                                               "verified_count": len(claims.get("verified_claims", []))},
        "artifacts": [{"path": rel(p), "sha256": sha256(p)} for p in
                      [MODELS_DIR / "qi_c1_vessel_type.txt", MODELS_DIR / "qi_c1.txt", MODELS_DIR / "model_real_04.txt",
                       MODELS_DIR / "conformal_quantiles.json", FUELS_CONFIG, PARETO_CSV]],
    }
    with AUDIT_LOCK:
        total = _CON.execute("SELECT COUNT(*), COUNT(DISTINCT session_id) FROM audit_events").fetchone()
    return {
        "session": {"label": f"CURRENT SESSION {SESSION_ID} — persisted to SQLite (append-only, not cryptographically sealed)",
                    "session_id": SESSION_ID, "events": audit_events()},
        "persisted": {"label": "PRIOR SESSIONS — earlier API runs from the same SQLite ledger",
                      "database": str(AUDIT_DB.relative_to(REPO_ROOT)) if AUDIT_DB.is_relative_to(REPO_ROOT) else str(AUDIT_DB),
                      "total_events": total[0], "total_sessions": total[1],
                      "events": audit_events(current_session=False, limit=200)},
        "historical": historical,
    }


# --------------------------------------------------------------------------- routes: demo

DEMO_SCENES = [
    (1, "Normal Poseidon cruise"), (2, "High operating demand"), (3, "Slow steaming"),
    (4, "Alternative fuel scenarios"), (5, "OOD storm"), (6, "Runtime failure / fallback"),
    (7, "Fleet optimization"), (8, "Vessel-type-aware prediction"), (9, "Operational cost"),
    (10, "Lifecycle WtW GHG"), (11, "Pareto trade-offs"),
]


@app.get("/api/demo/scenes")
def demo_scenes() -> Dict[str, Any]:
    return {"source": "scripts/demo_scenarios.py (verified scene inputs)", "mode": "DEMO — SIMULATION",
            "scenes": [{"id": i, "title": t} for i, t in DEMO_SCENES]}


class _CrashBooster:
    def predict(self, *args, **kwargs):
        raise RuntimeError("Injected QI booster fault (demo)")


@app.post("/api/demo/scenes/{scene_id}")
def run_demo_scene(scene_id: int) -> Dict[str, Any]:
    s1 = copy.deepcopy(demo.SCENE1_INPUT)
    poseidon = vessel_or_404("CPS_Poseidon")
    if scene_id == 1:
        data = {"prediction": predict_point(s1)}
    elif scene_id == 2:
        base = predict_point(s1)
        high = predict_point({**s1, "stw_kn": 19.5, "sog_kn": 19.5, "wind_speed_ms": 10.0, "wave_height_m": 2.0})
        data = {"baseline": base, "high_demand": high}
    elif scene_id == 3:
        data = {"baseline_18kn": predict_point({**s1, "stw_kn": 18.0, "sog_kn": 18.0}),
                "slow_15kn": predict_point({**s1, "stw_kn": 15.0, "sog_kn": 15.0})}
    elif scene_id == 4:
        data = fuels("CPS_Poseidon", 14.5, 14.5, 0.0)
    elif scene_id == 5:
        data = {"prediction": predict_point(copy.deepcopy(demo.OOD_STORM_INPUT))}
    elif scene_id == 6:
        faulty = copy.copy(PREDICTOR)  # shallow copy: the shared predictor is never mutated
        faulty.qi_c1_booster = _CrashBooster()
        faulty.qi_c1_vessel_type_booster = _CrashBooster()
        res = faulty.predict_fuel_with_uncertainty(s1, raise_on_error=False)
        data = {"prediction": {"input": s1, "result": jsonable(res), "trust": classify_trust(res, s1)},
                "injected_fault": "QI-C1 and QI-C1-vessel-type boosters raise RuntimeError"}
    elif scene_id == 7:
        from run_multiobjective_tradeoffs import FORMULATIONS
        data = {"solution": run_optimizer("Hybrid_QI_A5", demo.OPT_SEED, demo.OPT_BUDGET, list(FORMULATIONS["D_Fuel_Cost_GHG"])),
                "config": {"algorithm": "Hybrid_QI_A5", "seed": demo.OPT_SEED, "budget": demo.OPT_BUDGET,
                           "formulation": "D_Fuel_Cost_GHG"}}
    elif scene_id == 8:
        data = {"vessels": [predict_point({**s1, "vessel_id": vid, "vessel_type": vt, "displacement_t": disp,
                                           "draft_m": draft, "stw_kn": 14.0, "sog_kn": 14.0, "water_depth_m": 50.0})
                            for vid, vt, disp, draft in demo.VESSEL_TYPE_SCENE]}
    elif scene_id == 9:
        # Same two configurations as scripts/demo_scenarios.py Scene 9 (stated baseline rates).
        data = {"fuel_focus_12kn": voyage(poseidon, 2100.0, 12.0, "vlsfo", False, 6.0, 300.0, 24.0),
                "cost_focus_14_5kn_ops": voyage(poseidon, 2750.0, 14.5, "vlsfo", True, 6.0, 300.0, 24.0),
                "basis": "SCENARIO — baseline fuel rates are stated inputs of the verified demo scene"}
    elif scene_id == 10:
        data = {"fuels": [{"fuel": f, "label": label, "shore_power": shore,
                           "result": voyage({**poseidon, "hotel_load_kw": 1000.0}, 2500.0, 14.0, f, shore, 4.0, 250.0, 20.0)}
                          for f, label, shore in demo.LIFECYCLE_FUEL_SCENARIOS],
                "basis": "SCENARIO ESTIMATE — 2500 kg/h VLSFO baseline is a stated input of the verified demo scene"}
    elif scene_id == 11:
        data = pareto()
    else:
        raise HTTPException(404, f"Unknown scene {scene_id}")
    trust = data.get("prediction", {}).get("trust") if isinstance(data.get("prediction"), dict) else None
    record("DEMO_SCENE", scene_id=scene_id, title=dict(DEMO_SCENES)[scene_id], mode="DEMO — SIMULATION",
           **({"trust": trust} if trust else {}))
    return {"scene_id": scene_id, "title": dict(DEMO_SCENES)[scene_id], "mode": "DEMO — SIMULATION",
            "data": jsonable(data)}
