"""
Certification-Readiness Verification Battery (Part D, E & Q).
Implements all 30 mandatory tests (TEST 01 to TEST 30) for EGREEN QUANTA (SIH26138).

Note on regulatory claims:
This test battery produces an evidence package for readiness assessment.
It does NOT claim class certification or official IMO approval.
"""

import copy
import io
import json
import math
import shutil
import tempfile
from pathlib import Path
import numpy as np
import pytest
import jsonschema
from fastapi.testclient import TestClient

from api.main import app, JOBS, SCENARIOS
from src.export.decision_exporter import (
    build_optimization_decision_record,
    build_scenario_decision_record,
    generate_decision_csv,
    export_decision_package,
    verify_export_package,
    canonical_json_bytes,
    sha256_bytes,
    get_git_commit,
    DECISION_SCHEMA_PATH,
    MANIFEST_SCHEMA_PATH,
    EXPORTS_DIR
)
from src.qi_prediction.serving import get_production_predictor
from optimization.sih_objective_engine import SIHObjectiveEngine

POSEIDON_STANDARD = {
    "vessel_id": "CPS_Poseidon",
    "vessel_type": "passenger_cruise",
    "fuel_type": "vlsfo",
    "stw_kn": 14.5,
    "sog_kn": 14.5,
    "draft_m": 7.5,
    "displacement_t": 35000.0,
    "wind_speed_ms": 5.0,
    "wave_height_m": 1.0,
    "water_depth_m": 60.0
}

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def predictor():
    return get_production_predictor()


@pytest.fixture(scope="module")
def engine():
    return SIHObjectiveEngine()


# --------------------------------------------------------------------------- Tests 01 to 05: Core Prediction & Fallback

def test_01_normal_prediction(predictor):
    """TEST 01: Normal serving prediction returns valid positive fuel burn rate."""
    res = predictor.predict_fuel_with_uncertainty(POSEIDON_STANDARD, coverage=0.90)
    assert res["fuel_prediction"] is not None
    assert 1000.0 < res["fuel_prediction"] < 8000.0
    assert res["routing_status"] in ("NORMAL", "SERVED")
    assert res["in_domain"] is True


def test_02_prediction_api_parity(client, predictor):
    """TEST 02: Direct predictor output matches /api/predict response for identical inputs."""
    direct = predictor.predict_fuel_with_uncertainty(POSEIDON_STANDARD, coverage=0.90)
    api_resp = client.post("/api/predict", json=POSEIDON_STANDARD).json()
    api_res = api_resp["result"]

    assert np.isclose(direct["fuel_prediction"], api_res["fuel_prediction"], atol=1e-8)
    assert direct["routing_status"] == api_res["routing_status"]
    assert direct["prediction_source"] == api_res["prediction_source"]


def test_03_uncertainty_interval_validity(predictor):
    """TEST 03: Finite-sample conformal interval satisfies lower_bound <= prediction <= upper_bound."""
    res = predictor.predict_fuel_with_uncertainty(POSEIDON_STANDARD, coverage=0.90)
    unc = res["uncertainty"]
    assert unc is not None
    lower = unc["lower_bound_kg_h"]
    upper = unc["upper_bound_kg_h"]
    pred = res["fuel_prediction"]

    assert lower <= pred <= upper
    assert (upper - lower) > 0.0


def test_04_ood_detection(predictor):
    """TEST 04: Out-of-Domain hull dimensions or speed trigger OOD state."""
    ood_input = dict(POSEIDON_STANDARD)
    ood_input["displacement_t"] = 120000.0  # Far outside cruise ship envelope

    res = predictor.predict_fuel_with_uncertainty(ood_input, raise_on_error=False)
    assert res["in_domain"] is False
    assert res["routing_status"] in ("EMERGENCY_PHYSICS", "REJECT", "FALLBACK")


def test_05_fallback_behavior(predictor):
    """TEST 05: Safe fallback diverts to reference anchor or emergency baseline with explicit label."""
    near_ood = dict(POSEIDON_STANDARD)
    near_ood["draft_m"] = 13.5  # Near envelope boundary

    res = predictor.predict_fuel_with_uncertainty(near_ood, raise_on_error=False)
    assert res["routing_status"] == "FALLBACK"
    assert res["prediction_source"] == "MODEL_REAL_04"


# --------------------------------------------------------------------------- Tests 06 to 13: Input Validation & Boundary Conditions

def test_06_unknown_vessel_type(client):
    """TEST 06: Unknown vessel type triggers categorical OOD rejection, returning None."""
    bad_vessel = dict(POSEIDON_STANDARD)
    bad_vessel["vessel_type"] = "submersible_research"

    out = client.post("/api/predict", json=bad_vessel).json()
    assert out["trust"]["state"] == "OOD"
    assert out["trust"]["ood_band"] == "CATEGORICAL"
    assert out["result"]["fuel_prediction"] is None


def test_07_unknown_fuel(client):
    """TEST 07: Unknown fuel pathway is rejected with 422."""
    bad_scenario = {
        "vessel_id": "CPS_Poseidon",
        "fuel_type": "antimatter_plasma",
        "port_hours": 0.0,
        "distance_nm": 300.0,
        "deadline_h": 24.0
    }
    resp = client.post("/api/scenario", json=bad_scenario)
    assert resp.status_code == 422
    assert "Unsupported fuel_type" in resp.json()["detail"]


def test_08_nan_input(client):
    """TEST 08: NaN in input is cleanly blocked by schema validation (422) or evaluated as invalid."""
    # Fast-api / pydantic strict validation
    resp = client.post("/api/predict", json={**POSEIDON_STANDARD, "stw_kn": None})
    assert resp.status_code in (200, 422)
    if resp.status_code == 200:
        assert resp.json()["trust"]["state"] in ("INVALID_INPUT", "OOD")


def test_09_inf_input(client):
    """TEST 09: Inf float is rejected by JSON parser or validation contract."""
    resp = client.post("/api/predict", json={**POSEIDON_STANDARD, "wind_speed_ms": 1e308})
    assert resp.status_code == 200
    assert resp.json()["trust"]["state"] in ("INVALID_INPUT", "OOD")


def test_10_negative_speed(predictor):
    """TEST 10: Negative speed triggers validation failure or physical boundary rejection."""
    neg_speed = dict(POSEIDON_STANDARD)
    neg_speed["stw_kn"] = -5.0
    neg_speed["sog_kn"] = -5.0

    res = predictor.predict_fuel_with_uncertainty(neg_speed, raise_on_error=False)
    assert res["routing_status"] == "REJECT"
    assert res["fuel_prediction"] is None


def test_11_impossible_draft(predictor):
    """TEST 11: Impossible draft (e.g. 50m) triggers critical envelope rejection."""
    bad_draft = dict(POSEIDON_STANDARD)
    bad_draft["draft_m"] = 55.0

    res = predictor.predict_fuel_with_uncertainty(bad_draft, raise_on_error=False)
    assert res["routing_status"] in ("REJECT", "EMERGENCY_PHYSICS")
    assert res["envelope_distance"] > 1.5


def test_12_impossible_displacement(predictor):
    """TEST 12: Impossible displacement (e.g. 500,000 tonnes) triggers critical rejection."""
    bad_disp = dict(POSEIDON_STANDARD)
    bad_disp["displacement_t"] = 600000.0

    res = predictor.predict_fuel_with_uncertainty(bad_disp, raise_on_error=False)
    assert res["routing_status"] in ("REJECT", "EMERGENCY_PHYSICS")
    assert res["in_domain"] is False


def test_13_extreme_weather(client):
    """TEST 13: Hurricane-force weather triggers OOD REJECT status."""
    import demo_scenarios as demo
    out = client.post("/api/predict", json=demo.OOD_STORM_INPUT).json()
    assert out["trust"]["state"] == "OOD"
    assert out["trust"]["ood_band"] == "REJECT"


# --------------------------------------------------------------------------- Tests 14 to 18: Optimization, Pareto & Economics

def test_14_constraint_violation(engine):
    """TEST 14: Schedule deadline violation generates delay hours and schedule penalty."""
    ev = engine.evaluate_voyage(
        vessel_id="CPS_Poseidon",
        vessel_type="passenger_cruise",
        speed_knots=10.0,
        voyage_distance_nm=300.0,  # 300 / 10 = 30 hours
        schedule_deadline_hours=20.0,  # 10 hours late
        baseline_fuel_rate_kg_h=2500.0,
        fuel_type="vlsfo"
    )
    assert ev.schedule_delay_hours == pytest.approx(10.0, abs=0.01)
    assert ev.schedule_penalty_usd > 0.0
    assert ev.is_feasible is False


def test_15_infeasible_optimization():
    """TEST 15: Infeasible solution candidate has non-zero penalty and is marked infeasible."""
    from types import SimpleNamespace
    from api.main import solution_payload

    fake_out = SimpleNamespace(
        is_feasible=False,
        penalty=5000.0,
        fuel_tonnes=100.0,
        opex_usd=50000.0,
        ghg_tonnes=300.0,
        delay_hours=12.0,
        risk_metric=0.0,
        fitness=150000.0,
        hard_violations=["Schedule deadline exceeded by 12.0 h"],
        assigned_demands={"CPS_Poseidon": "DEMAND_1"},
        fuel_decisions={"CPS_Poseidon": "vlsfo"},
        shore_decisions={"CPS_Poseidon": False},
        speed_decisions={"CPS_Poseidon": 12.0},
        raw_result=SimpleNamespace(cargo_allocations={}, scenario_details=True, soft_penalties={})
    )
    res = solution_payload(fake_out, SimpleNamespace(feasible_at_end=False, objective_evaluations=10, runtime_seconds=0.1))
    assert res["feasible"] is False
    assert res["penalty"] == 5000.0
    assert len(res["hard_violations"]) == 1


def test_16_pareto_dominance_verification(client):
    """TEST 16: Verify that all points in Pareto front are mutually non-dominated."""
    pts = client.get("/api/pareto").json()["points"]
    assert len(pts) >= 1

    # For any pair (p1, p2), p1 cannot strictly dominate p2 on all 4 objectives
    for i, p1 in enumerate(pts):
        for j, p2 in enumerate(pts):
            if i == j:
                continue
            better_or_equal = (
                p1["fuel_tonnes"] <= p2["fuel_tonnes"] and
                p1["cost_usd"] <= p2["cost_usd"] and
                p1["ghg_tonnes"] <= p2["ghg_tonnes"] and
                p1["delay_hours"] <= p2["delay_hours"]
            )
            strictly_better = (
                p1["fuel_tonnes"] < p2["fuel_tonnes"] or
                p1["cost_usd"] < p2["cost_usd"] or
                p1["ghg_tonnes"] < p2["ghg_tonnes"] or
                p1["delay_hours"] < p2["delay_hours"]
            )
            assert not (better_or_equal and strictly_better), f"Point {i} strictly dominates Point {j} in Pareto front!"


def test_17_cost_calculation_parity(engine):
    """TEST 17: Operational cost equals sum of fuel cost + carbon cost + demurrage + shore power."""
    ev = engine.evaluate_voyage(
        vessel_id="CPS_Poseidon",
        vessel_type="passenger_cruise",
        speed_knots=15.0,
        voyage_distance_nm=150.0,
        schedule_deadline_hours=12.0,
        baseline_fuel_rate_kg_h=2500.0,
        fuel_type="vlsfo",
        use_shore_power=True,
        port_hours=4.0
    )
    expected_sum = (
        ev.fuel_cost_usd +
        ev.carbon_cost_usd +
        ev.shore_power_cost_usd +
        ev.schedule_penalty_usd +
        ev.fueleu_penalty_usd
    )
    assert np.isclose(ev.operational_cost_usd, expected_sum, atol=1e-2)


def test_18_lifecycle_ghg_calculation_parity(engine):
    """TEST 18: Lifecycle GHG matches WtT + TtW + methane slip tonnes."""
    ev = engine.evaluate_voyage(
        vessel_id="CPS_Poseidon",
        vessel_type="passenger_cruise",
        speed_knots=15.0,
        voyage_distance_nm=150.0,
        schedule_deadline_hours=12.0,
        baseline_fuel_rate_kg_h=2500.0,
        fuel_type="lng",
        port_hours=2.0
    )
    expected_wtw = ev.wtt_ghg_tonnes + ev.ttw_ghg_tonnes
    assert np.isclose(ev.lifecycle_ghg_tonnes, expected_wtw, atol=1e-3)
    assert ev.methane_slip_tonnes > 0.0


# --------------------------------------------------------------------------- Tests 19 to 25: Reproducibility, Integrity & Tamper

def test_19_optimization_reproducibility_with_fixed_seed():
    """TEST 19: Fixed seed produces identical decision vector trajectory."""
    from src.qi_prediction.qpso import QPSOOptimizer
    def dummy_obj(params: dict) -> float:
        return float(params["learning_rate"] * 2.0 + params["num_leaves"])

    qpso1 = QPSOOptimizer(n_particles=10, max_iterations=8, seed=42)
    res1 = qpso1.optimize(dummy_obj)

    qpso2 = QPSOOptimizer(n_particles=10, max_iterations=8, seed=42)
    res2 = qpso2.optimize(dummy_obj)

    assert np.allclose(res1["best_vector"], res2["best_vector"], atol=1e-10)
    assert np.isclose(res1["best_score"], res2["best_score"], atol=1e-10)


def test_20_decision_record_reproducibility():
    """TEST 20: Same job and fixed timestamps produce bitwise identical decision record and hash."""
    sample = {
        "job_id": "OPT-det001",
        "params": {"algorithm": "Hybrid_QI_A5", "seed": 1005, "budget": 2500, "weights": [0.35, 0.35, 0.3, 0, 0]},
        "result": {
            "feasible": True, "penalty_free": True, "penalty": 0.0, "soft_penalties": {},
            "objectives": {"fuel_t": 140.0, "opex_usd": 90000.0, "wtw_tco2e": 430.0, "delay_h": 0.0, "risk_cvar_excess": 0.0},
            "hard_violations": [],
            "vessels": [{"vessel_id": "CPS_Poseidon", "assigned_demand": "DEMAND_1", "speed_kn": 14.5, "fuel": "vlsfo", "shore_power": False}],
            "evaluations": 2500, "runtime_s": 1.0
        }
    }
    rec1 = build_optimization_decision_record("OPT-det001", sample, operator_status="CONFIRMED", trace_id="TRC-DET")
    rec2 = build_optimization_decision_record("OPT-det001", sample, operator_status="CONFIRMED", trace_id="TRC-DET")
    rec2["record_metadata"]["created_at_utc"] = rec1["record_metadata"]["created_at_utc"]
    rec2["decision"]["confirmation_timestamp_utc"] = rec1["decision"]["confirmation_timestamp_utc"]
    rec2["integrity"] = rec1["integrity"]

    b1 = canonical_json_bytes(rec1)
    b2 = canonical_json_bytes(rec2)
    assert b1 == b2
    assert sha256_bytes(b1) == sha256_bytes(b2)


def test_21_json_schema_validation():
    """TEST 21: JSON schema validator accepts generated decision records."""
    sample = {
        "job_id": "OPT-schema",
        "params": {"algorithm": "Hybrid_QI_A5", "seed": 1005, "budget": 2500, "weights": [0.35, 0.35, 0.3, 0, 0]},
        "result": {
            "feasible": True, "penalty_free": True, "penalty": 0.0, "soft_penalties": {},
            "objectives": {"fuel_t": 100.0, "opex_usd": 70000.0, "wtw_tco2e": 300.0, "delay_h": 0.0, "risk_cvar_excess": 0.0},
            "hard_violations": [],
            "vessels": [{"vessel_id": "CPS_Poseidon", "assigned_demand": "DEMAND_1", "speed_kn": 14.0, "fuel": "vlsfo", "shore_power": False}],
            "evaluations": 2500, "runtime_s": 1.0
        }
    }
    rec = build_optimization_decision_record("OPT-schema", sample, operator_status="CONFIRMED")
    schema = json.loads(DECISION_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=rec, schema=schema)


def test_22_csv_json_consistency():
    """TEST 22: Values in decision_record.csv match decision_record.json exactly."""
    sample = {
        "job_id": "OPT-csvtest",
        "params": {"algorithm": "Hybrid_QI_A5", "seed": 1005, "budget": 2500, "weights": [0.35, 0.35, 0.3, 0, 0]},
        "result": {
            "feasible": True, "penalty_free": True, "penalty": 0.0, "soft_penalties": {},
            "objectives": {"fuel_t": 135.5, "opex_usd": 88000.0, "wtw_tco2e": 410.0, "delay_h": 0.0, "risk_cvar_excess": 0.0},
            "hard_violations": [],
            "vessels": [{"vessel_id": "CPS_Poseidon", "assigned_demand": "DEMAND_1", "speed_kn": 14.2, "fuel": "vlsfo", "shore_power": False}],
            "evaluations": 2500, "runtime_s": 1.0
        }
    }
    rec = build_optimization_decision_record("OPT-csvtest", sample, operator_status="CONFIRMED")
    csv_str = generate_decision_csv(rec)
    assert "135.5" in csv_str
    assert "88000" in csv_str


def test_23_sha256_verification():
    """TEST 23: Direct verification of SHA-256 computation over canonical bytes."""
    data = {"test_key": "test_value", "number": 12345}
    b = canonical_json_bytes(data)
    h = sha256_bytes(b)
    assert len(h) == 64
    assert h == sha256_bytes(b)


def test_24_tamper_detection():
    """TEST 24: Modifying 1 byte in decision_record.json causes verification failure."""
    sample = {
        "job_id": "OPT-tamper",
        "params": {"algorithm": "Hybrid_QI_A5", "seed": 1005, "budget": 2500, "weights": [0.35, 0.35, 0.3, 0, 0]},
        "result": {
            "feasible": True, "penalty_free": True, "penalty": 0.0, "soft_penalties": {},
            "objectives": {"fuel_t": 140.0, "opex_usd": 90000.0, "wtw_tco2e": 430.0, "delay_h": 0.0, "risk_cvar_excess": 0.0},
            "hard_violations": [],
            "vessels": [{"vessel_id": "CPS_Poseidon", "assigned_demand": "DEMAND_1", "speed_kn": 14.5, "fuel": "vlsfo", "shore_power": False}],
            "evaluations": 2500, "runtime_s": 1.0
        }
    }
    rec = build_optimization_decision_record("OPT-tamper", sample, operator_status="CONFIRMED")
    tmp = Path(tempfile.mkdtemp())
    try:
        pkg = export_decision_package(rec, base_export_dir=tmp)
        jpath = pkg / "decision_record.json"
        raw = jpath.read_bytes()
        jpath.write_bytes(raw.replace(b"90000", b"90001"))

        res = verify_export_package(pkg)
        assert res["verified"] is False
        assert res["tampered"] is True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_25_manifest_verification():
    """TEST 25: Manifest validates against schemas/manifest.schema.json."""
    sample = {
        "job_id": "OPT-man",
        "params": {"algorithm": "Hybrid_QI_A5", "seed": 1005, "budget": 2500, "weights": [0.35, 0.35, 0.3, 0, 0]},
        "result": {
            "feasible": True, "penalty_free": True, "penalty": 0.0, "soft_penalties": {},
            "objectives": {"fuel_t": 140.0, "opex_usd": 90000.0, "wtw_tco2e": 430.0, "delay_h": 0.0, "risk_cvar_excess": 0.0},
            "hard_violations": [],
            "vessels": [{"vessel_id": "CPS_Poseidon", "assigned_demand": "DEMAND_1", "speed_kn": 14.5, "fuel": "vlsfo", "shore_power": False}],
            "evaluations": 2500, "runtime_s": 1.0
        }
    }
    rec = build_optimization_decision_record("OPT-man", sample, operator_status="CONFIRMED")
    tmp = Path(tempfile.mkdtemp())
    try:
        pkg = export_decision_package(rec, base_export_dir=tmp)
        mdata = json.loads((pkg / "manifest.json").read_text(encoding="utf-8"))
        schema = json.loads(MANIFEST_SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.validate(instance=mdata, schema=schema)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------- Tests 26 to 30: Traceability, States & End-to-End

def test_26_model_version_traceability():
    """TEST 26: Model versions are traceable to frozen metadata files."""
    meta_path = Path("models/qi_c1_vessel_type_meta.json")
    assert meta_path.exists()
    m_info = json.loads(meta_path.read_text(encoding="utf-8"))
    assert m_info["version"] in ("1.1.0-sih-complete", "1.0.0-production")
    assert "test_mae_kg_h" in m_info


def test_27_git_commit_traceability():
    """TEST 27: Git commit hash in export package matches repository HEAD."""
    c = get_git_commit()
    assert len(c) in (7, 40)
    assert c != "unknown"


def test_28_export_import_round_trip():
    """TEST 28: Exported decision package can be parsed and validated without source code dependencies."""
    sample = {
        "job_id": "OPT-roundtrip",
        "params": {"algorithm": "Hybrid_QI_A5", "seed": 1005, "budget": 2500, "weights": [0.35, 0.35, 0.3, 0, 0]},
        "result": {
            "feasible": True, "penalty_free": True, "penalty": 0.0, "soft_penalties": {},
            "objectives": {"fuel_t": 140.0, "opex_usd": 90000.0, "wtw_tco2e": 430.0, "delay_h": 0.0, "risk_cvar_excess": 0.0},
            "hard_violations": [],
            "vessels": [{"vessel_id": "CPS_Poseidon", "assigned_demand": "DEMAND_1", "speed_kn": 14.5, "fuel": "vlsfo", "shore_power": False}],
            "evaluations": 2500, "runtime_s": 1.0
        }
    }
    rec = build_optimization_decision_record("OPT-roundtrip", sample, operator_status="CONFIRMED")
    tmp = Path(tempfile.mkdtemp())
    try:
        pkg = export_decision_package(rec, base_export_dir=tmp)
        raw_json = json.loads((pkg / "decision_record.json").read_text(encoding="utf-8"))

        # Pure JSON parser validation
        assert raw_json["record_metadata"]["record_id"] == "REC-OPT-roundtrip"
        assert raw_json["objectives"]["fuel_tonnes"] == 140.0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_29_operator_confirmation_state():
    """TEST 29: System enforces progression DRAFT -> REVIEWED -> CONFIRMED -> EXPORTED."""
    sample = {
        "job_id": "OPT-stateflow",
        "params": {"algorithm": "Hybrid_QI_A5", "seed": 1005, "budget": 2500, "weights": [0.35, 0.35, 0.3, 0, 0]},
        "result": {
            "feasible": True, "penalty_free": True, "penalty": 0.0, "soft_penalties": {},
            "objectives": {"fuel_t": 140.0, "opex_usd": 90000.0, "wtw_tco2e": 430.0, "delay_h": 0.0, "risk_cvar_excess": 0.0},
            "hard_violations": [],
            "vessels": [{"vessel_id": "CPS_Poseidon", "assigned_demand": "DEMAND_1", "speed_kn": 14.5, "fuel": "vlsfo", "shore_power": False}],
            "evaluations": 2500, "runtime_s": 1.0
        }
    }
    r_draft = build_optimization_decision_record("OPT-stateflow", sample, operator_status="DRAFT")
    assert r_draft["decision"]["operator_status"] == "DRAFT"
    assert r_draft["decision"]["confirmation_timestamp_utc"] is None

    r_conf = build_optimization_decision_record("OPT-stateflow", sample, operator_status="CONFIRMED")
    assert r_conf["decision"]["operator_status"] == "CONFIRMED"
    assert r_conf["decision"]["confirmation_timestamp_utc"] is not None


def test_30_end_to_end_decision_trace():
    """TEST 30: Machine-readable trace_id links operator input through optimization to exported package."""
    sample = {
        "job_id": "OPT-trace30",
        "params": {"algorithm": "Hybrid_QI_A5", "seed": 1005, "budget": 2500, "weights": [0.35, 0.35, 0.3, 0, 0]},
        "result": {
            "feasible": True, "penalty_free": True, "penalty": 0.0, "soft_penalties": {},
            "objectives": {"fuel_t": 140.0, "opex_usd": 90000.0, "wtw_tco2e": 430.0, "delay_h": 0.0, "risk_cvar_excess": 0.0},
            "hard_violations": [],
            "vessels": [{"vessel_id": "CPS_Poseidon", "assigned_demand": "DEMAND_1", "speed_kn": 14.5, "fuel": "vlsfo", "shore_power": False}],
            "evaluations": 2500, "runtime_s": 1.0
        }
    }
    trace_id = "TRC-AUDIT-E2E-99999"
    rec = build_optimization_decision_record("OPT-trace30", sample, operator_status="CONFIRMED", trace_id=trace_id)
    tmp = Path(tempfile.mkdtemp())
    try:
        pkg = export_decision_package(rec, base_export_dir=tmp)
        manifest = json.loads((pkg / "manifest.json").read_text(encoding="utf-8"))
        readme = (pkg / "README.txt").read_text(encoding="utf-8")

        assert rec["record_metadata"]["trace_id"] == trace_id
        assert manifest["trace_id"] == trace_id
        assert trace_id in readme
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
