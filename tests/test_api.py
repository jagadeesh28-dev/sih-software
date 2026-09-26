"""
Integration tests for the HMI API (api/main.py) against the real backend modules.
Covers prediction trust states, scenario provenance, fuels, Pareto, optimizer jobs,
human-in-the-loop decisions, alerts, audit and every demo scene.
"""

import json
import os
import sqlite3
import tempfile
import time

import pytest
from fastapi.testclient import TestClient

# Isolated audit ledger for tests (must be set before api.main is imported).
os.environ["EQ_AUDIT_DB"] = os.path.join(tempfile.mkdtemp(prefix="eq_audit_"), "audit.sqlite")

from api.main import app  # noqa: E402

POSEIDON = {"vessel_id": "CPS_Poseidon", "vessel_type": "passenger_cruise", "fuel_type": "vlsfo",
            "stw_kn": 14.5, "sog_kn": 14.5, "draft_m": 7.5, "displacement_t": 35000.0,
            "wind_speed_ms": 5.0, "wave_height_m": 1.0, "water_depth_m": 60.0}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def evaluator_ready(client):
    for _ in range(240):
        s = client.get("/api/status").json()
        if s["evaluator_ready"]:
            return True
        assert s["evaluator_error"] is None, s["evaluator_error"]
        time.sleep(0.5)
    pytest.fail("fleet evaluator did not become ready")


def test_status_reports_no_live_feed(client):
    s = client.get("/api/status").json()
    assert s["live_feed_connected"] is False and s["data_mode"] == "SIMULATION"
    assert s["fleet_count"] == 3 and len(s["fleet_trust"]) == 3


def test_fleet_predictions_come_from_backend(client):
    f = client.get("/api/fleet").json()
    assert f["kpis"]["vessels"] == 3
    for row in f["vessels"]:
        assert row["prediction"]["result"]["fuel_prediction"] > 0
        assert row["schedule"] is None  # not tracked: never invented


def test_predict_normal_invalid_and_unsupported_vessel(client):
    ok = client.post("/api/predict", json=POSEIDON).json()
    assert ok["trust"]["state"] in ("NORMAL", "WARNING") and ok["result"]["fuel_prediction"] > 0

    bad = client.post("/api/predict", json={"stw_kn": 14.0}).json()
    assert bad["trust"]["state"] == "INVALID_INPUT" and bad["result"]["fuel_prediction"] is None
    assert bad["trust"]["ood_band"] == "NOT_EVALUATED"

    unk = client.post("/api/predict", json={**POSEIDON, "vessel_type": "bulk_carrier"}).json()
    assert unk["trust"]["state"] == "OOD" and unk["trust"]["ood_band"] == "CATEGORICAL"
    assert unk["result"]["fuel_prediction"] is None

    near = client.post("/api/predict", json={**POSEIDON, "draft_m": 13.5}).json()
    assert near["trust"]["state"] == "WARNING" and near["trust"]["fallback_label"] == "MODEL-REAL-04 FALLBACK"
    assert "draft_m" in near["trust"]["reason"]


def test_predict_rejects_malformed_payload(client):
    assert client.post("/api/predict", json={"stw_kn": "fast"}).status_code == 422
    assert client.post("/api/predict", json={"unknown_field": 1}).status_code == 422


def test_storm_is_never_normal(client):
    storm = {**POSEIDON, "stw_kn": 33.0, "sog_kn": 32.0, "draft_m": 22.0, "displacement_t": 160000.0,
             "wind_speed_ms": 48.0, "wave_height_m": 14.0, "water_depth_m": 15.0}
    out = client.post("/api/predict", json=storm).json()
    assert out["trust"]["state"] == "OOD" and out["trust"]["ood_band"] == "REJECT"
    assert out["result"]["fuel_prediction"] is None
    assert "displacement_t" in out["trust"]["reason"]


def test_ood_physics_estimate_is_labelled_not_a_recommendation(client):
    out = client.post("/api/predict", json={**POSEIDON, "displacement_t": 110000.0}).json()
    assert out["trust"]["ood_band"] == "OOD" and out["result"]["prediction_source"] == "PHYSICS_EMERGENCY"
    assert "NOT A RECOMMENDATION" in out["trust"]["fallback_label"]


def test_scenario_provenance_and_validation(client):
    r = client.post("/api/scenario", json={"vessel_id": "CPS_Triton", "base": "dataset_latest",
                                           "overrides": {"stw_kn": 12}, "fuel_type": "bio_methanol"}).json()
    assert r["provenance"]["stw_kn"] == "SCENARIO INPUT" and r["provenance"]["sog_kn"] == "SCENARIO INPUT"
    assert r["provenance"]["draft_m"].startswith("MEASURED")
    assert r["voyage"]["fuel_type"] == "bio_methanol" and r["voyage"]["fuel_t"] > 0
    assert client.post("/api/scenario", json={"vessel_id": "CPS_Triton", "fuel_type": "unobtainium"}).status_code == 422
    assert client.post("/api/scenario", json={"vessel_id": "CPS_Triton", "overrides": {"cargo": 5}}).status_code == 422
    assert client.post("/api/scenario", json={"vessel_id": "NOPE"}).status_code == 404


def test_fuels_are_labelled_and_energy_invariant(client):
    f = client.get("/api/fuels", params={"vessel_id": "OSS_Ceto", "speed_kn": 12}).json()
    bases = {r["key"]: r["basis"] for r in f["rows"]}
    assert bases["vlsfo"] == "MODEL PREDICTION"
    assert all(b == "SCENARIO ESTIMATE" for k, b in bases.items() if k != "vlsfo")
    assert all(r["measured_telemetry"] is False for r in f["rows"])
    energies = [r["result"]["energy_mj_h"] for r in f["rows"]]
    # Equal shaft energy across pathways (engine rounds fuel mass to 4 d.p.).
    assert max(energies) - min(energies) <= 1e-4 * max(energies)


def test_fuels_shore_comparison_is_backend_derived_and_signed_by_model(client):
    f = client.get("/api/fuels", params={"vessel_id": "CPS_Poseidon", "speed_kn": 14.5, "port_hours": 6}).json()
    rows = {r["key"]: r["result"] for r in f["rows"]}
    comp = {c["fuel"]: c for c in f["shore_comparison"]}
    assert rows["vlsfo"]["berth"]["source"] == "ONBOARD GENERATION" and rows["vlsfo+shore"]["berth"]["source"] == "SHORE POWER"
    assert rows["vlsfo+shore"]["berth"]["fuel_t"] == 0.0 < rows["vlsfo"]["berth"]["fuel_t"]
    d = rows["vlsfo+shore"]["ghg"]["wtw_tco2e"] - rows["vlsfo"]["ghg"]["wtw_tco2e"]
    assert abs(comp["vlsfo"]["delta_wtw_tco2e"] - d) < 1e-3
    for c in comp.values():
        expected = "REDUCES GHG" if c["delta_wtw_tco2e"] < 0 else "INCREASES GHG" if c["delta_wtw_tco2e"] > 0 else "NO GHG CHANGE"
        assert c["ghg_effect"] == expected
        assert c["onboard_berth"]["energy_kwh"] == c["shore_berth"]["energy_kwh"] > 0


def test_pareto_is_feasible_and_deduplicated(client):
    pts = client.get("/api/pareto").json()["points"]
    keys = [(p["fuel_tonnes"], p["cost_usd"], p["ghg_tonnes"], p["delay_hours"]) for p in pts]
    assert len(keys) == len(set(keys)) >= 2


def test_hard_violation_plan_reports_no_objectives(client, evaluator_ready):
    from types import SimpleNamespace
    import numpy as np
    import api.main as hmi
    from src.evaluator.common_evaluator import CommonFleetEvaluator
    xl, _ = hmi.EVALUATOR["value"].get_bounds()
    out = CommonFleetEvaluator(hmi.EVALUATOR["value"], max_budget=1).evaluate(xl.copy())  # all vessels unassigned
    sol = hmi.solution_payload(out, SimpleNamespace(feasible_at_end=False, objective_evaluations=1, runtime_seconds=0.0))
    assert sol["feasible"] is False and sol["penalty_free"] is False
    assert sol["objectives"] is None  # the fast-path placeholder vector is not a model output


def test_pareto_summary_states_point_count_without_ranking(client):
    p = client.get("/api/pareto").json()
    n = len(p["points"])
    expected = ("One non-dominated feasible solution identified under the current constraints." if n == 1
                else f"{n} non-dominated feasible solutions identified under the current constraints.")
    assert p["summary"] == expected
    assert all(pt["penalty"] <= 0.0 for pt in p["points"])
    assert "best" not in p["summary"].lower()


def test_pareto_resolve_reproduces_archive(client, evaluator_ready):
    r = client.post("/api/pareto/PS-01/resolve").json()
    assert r["reproduced"] is True and len(r["rerun"]["vessels"]) == 3


def test_optimizer_job_and_human_decision(client, evaluator_ready):
    job = client.post("/api/optimize", json={"algorithm": "DE", "seed": 1005, "budget": 1000,
                                             "weights": [0.35, 0.35, 0.3, 0, 0]}).json()
    for _ in range(200):
        job = client.get(f"/api/optimize/{job['job_id']}").json()
        if job["status"] in ("DONE", "ERROR"):
            break
        time.sleep(0.2)
    assert job["status"] == "DONE" and job["evaluations"] == 1000
    assert job["advisory"] == "ADVISORY — REQUIRES HUMAN ACCEPTANCE"
    if job["result"]["feasible"]:
        assert job["recommendation_status"] == "PENDING_REVIEW"
        d = client.post(f"/api/recommendations/{job['job_id']}/decision", json={"decision": "REJECT", "note": "t"})
        assert d.json()["recommendation_status"] == "REJECTED"
        again = client.post(f"/api/recommendations/{job['job_id']}/decision", json={"decision": "ACCEPT"})
        assert again.status_code == 409
    kinds = [e["kind"] for e in client.get("/api/audit").json()["session"]["events"]]
    assert "OPTIMIZATION" in kinds


def test_every_offered_algorithm_is_accepted_by_optimize(client):
    import api.main as hmi
    for alg in client.get("/api/optimizer/config").json()["algorithms"]:
        assert hmi.OptimizeRequest(algorithm=alg).algorithm == alg


def test_optimize_rejects_bad_weights(client):
    assert client.post("/api/optimize", json={"weights": [0, 0, 0, 0, 0]}).status_code == 422
    assert client.post("/api/optimize", json={"budget": 123}).status_code == 422


def test_alerts_and_audit_distinguish_session_from_history(client):
    client.post("/api/predict", json={"stw_kn": 14.0})
    alerts = client.get("/api/alerts").json()["alerts"]
    assert any(a["state"] == "INVALID_INPUT" for a in alerts)
    audit = client.get("/api/audit").json()
    assert audit["session"]["label"].startswith("CURRENT SESSION")
    assert audit["historical"]["label"].startswith("HISTORICAL EVIDENCE")


@pytest.mark.parametrize("scene", range(1, 12))
def test_demo_scenes_run_on_backend(client, evaluator_ready, scene):
    r = client.post(f"/api/demo/scenes/{scene}")
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "DEMO — SIMULATION"
    if scene == 5:
        assert body["data"]["prediction"]["trust"]["state"] == "OOD"
        assert body["data"]["prediction"]["result"]["fuel_prediction"] is None
    if scene == 6:
        t = body["data"]["prediction"]["trust"]
        assert t["state"] == "RUNTIME_FAILURE" and t["fallback_label"] == "MODEL-REAL-04 FALLBACK"
        events = client.get("/api/audit").json()["session"]["events"]
        assert events[-1]["kind"] == "DEMO_SCENE" and events[-1]["trust"]["state"] == "RUNTIME_FAILURE"
        assert any(a["state"] == "RUNTIME_FAILURE" for a in client.get("/api/alerts").json()["alerts"])
    if scene == 7:
        assert body["data"]["solution"]["objectives"]["fuel_t"] > 0


def test_audit_events_are_persisted_to_sqlite(client):
    client.post("/api/predict", json=POSEIDON)
    db = os.environ["EQ_AUDIT_DB"]
    con = sqlite3.connect(db)
    rows = con.execute("SELECT kind, ood_state, vessel_id, payload_json FROM audit_events WHERE kind='PREDICTION'").fetchall()
    con.close()
    assert rows and rows[-1][2] == "CPS_Poseidon" and rows[-1][1] in ("NORMAL", "WARNING")
    assert json.loads(rows[-1][3])["trust"]["state"] == rows[-1][1]


def test_prior_sessions_are_separated_from_current_session(client):
    con = sqlite3.connect(os.environ["EQ_AUDIT_DB"])
    cols = [r[1] for r in con.execute("PRAGMA table_info(audit_events)")]
    prior = {"event_id": "EVT-OLD-0001", "session_id": "S-PRIOR", "timestamp": "2026-01-01T00:00:00+00:00",
             "kind": "PREDICTION", "operator": "HMI operator (unauthenticated)"}
    row = {c: prior.get(c) for c in cols}
    row["payload_json"] = json.dumps(prior)
    con.execute(f"INSERT INTO audit_events VALUES ({', '.join('?' for _ in cols)})", [row[c] for c in cols])
    con.commit(); con.close()
    audit = client.get("/api/audit").json()
    assert all(e["session_id"] == audit["session"]["session_id"] for e in audit["session"]["events"])
    assert any(e["event_id"] == "EVT-OLD-0001" for e in audit["persisted"]["events"])
    assert "not cryptographically sealed" in audit["session"]["label"]


def test_optimizer_domain_is_inside_serving_envelope(client, evaluator_ready):
    """Every state the optimizer's DomainChecker accepts must be IN_DOMAIN for the serving guard."""
    import numpy as np
    import api.main as m
    from optimization.canonical_mapper import canonicalize_vessel_type, get_baseline_fuel_for_vessel
    from optimization.fleet_heterogeneous import FLEET_VESSELS, WEATHER_SCENARIOS
    surrogates = m.EVALUATOR["value"].surrogates
    worst, accepted = 0.0, 0
    for v in FLEET_VESSELS.values():
        for scen in WEATHER_SCENARIOS:
            for sp in np.linspace(0.5, v.max_speed_knots + 2, 60):
                state = {"stw_kn": sp, "sog_kn": sp, "draft_m": v.design_draft_m, "displacement_t": v.displacement_t,
                         "wind_speed_ms": scen.wind_speed_ms, "wind_direction_deg": scen.wind_direction_deg,
                         "wave_height_m": scen.wave_height_m, "wave_period_s": scen.wave_period_s,
                         "wave_direction_deg": 180.0, "current_speed_ms": scen.current_speed_ms,
                         "current_direction_deg": scen.current_direction_deg, "water_depth_m": scen.water_depth_m,
                         "vessel_type": canonicalize_vessel_type(v.class_family),
                         "fuel_type": get_baseline_fuel_for_vessel(v.vessel_id)}
                if surrogates[v.vessel_id].domain_checker.evaluate_point(state)["domain_status"] in ("IN_DOMAIN", "NEAR_BOUNDARY"):
                    accepted += 1
                    worst = max(worst, m.PREDICTOR.compute_envelope_distance(state))
    assert accepted > 0
    assert worst <= m.PREDICTOR.config.get("domain_guard", {}).get("envelope_distance_threshold_warning", 1.0)
