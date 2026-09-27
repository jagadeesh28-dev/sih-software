"""
Unit Tests for Seed Reproducibility (SIH26138 - Phase 6).
Verifies exact bitwise and trajectory reproducibility for QIEA, QPSO, and ML models.
"""

import numpy as np
import pytest
import lightgbm as lgb
from src.qi_prediction.qiea import QIEAFeatureSelector
from src.qi_prediction.qpso import QPSOOptimizer, HyperparameterSearchSpace


def test_qiea_seed_determinism():
    """Verify QIEA produces bitwise identical feature masks and trajectories under same seed."""
    def dummy_eval(mask: np.ndarray) -> float:
        return float(np.sum((mask - np.array([1, 0, 1, 0, 1, 1, 0, 0, 1, 0])) ** 2))

    qiea1 = QIEAFeatureSelector(population_size=8, max_generations=10, seed=42)
    res1 = qiea1.search(n_features=10, eval_fn=dummy_eval)

    qiea2 = QIEAFeatureSelector(population_size=8, max_generations=10, seed=42)
    res2 = qiea2.search(n_features=10, eval_fn=dummy_eval)

    assert np.array_equal(res1["best_mask"], res2["best_mask"])
    assert np.isclose(res1["best_score"], res2["best_score"], atol=1e-12)
    assert np.allclose(res1["convergence_history"], res2["convergence_history"], atol=1e-12)


def test_qpso_seed_determinism():
    """Verify QPSO produces identical vectors and convergence history under same seed."""
    dim = HyperparameterSearchSpace.get_dim()

    def dummy_obj(params: dict) -> float:
        return float(params["learning_rate"] * 2.0 + params["num_leaves"])

    qpso1 = QPSOOptimizer(n_particles=10, max_iterations=8, seed=42)
    res1 = qpso1.optimize(dummy_obj)

    qpso2 = QPSOOptimizer(n_particles=10, max_iterations=8, seed=42)
    res2 = qpso2.optimize(dummy_obj)

    assert np.allclose(res1["best_vector"], res2["best_vector"], atol=1e-10)
    assert np.isclose(res1["best_score"], res2["best_score"], atol=1e-10)
    assert np.allclose(res1["convergence_history"], res2["convergence_history"], atol=1e-10)


def test_lightgbm_seed_determinism():
    """Verify LightGBM model fits bitwise identically under fixed seed."""
    rng = np.random.default_rng(42)
    X = rng.normal(0, 1, size=(200, 5))
    y = X[:, 0] * 2.0 + X[:, 1]

    m1 = lgb.LGBMRegressor(n_estimators=30, random_state=42, n_jobs=1, verbose=-1)
    m1.fit(X, y)
    p1 = m1.predict(X)

    m2 = lgb.LGBMRegressor(n_estimators=30, random_state=42, n_jobs=1, verbose=-1)
    m2.fit(X, y)
    p2 = m2.predict(X)

    assert np.allclose(p1, p2, atol=1e-12)


def test_prediction_reproducibility():
    """Verify fuel prediction and conformal intervals reproduce exactly across runs."""
    from src.qi_prediction.serving import get_production_predictor
    p = get_production_predictor()
    point = {
        "vessel_id": "CPS_Poseidon",
        "vessel_type": "passenger_cruise",
        "stw_kn": 14.5,
        "sog_kn": 14.5,
        "draft_m": 7.5,
        "displacement_t": 35000.0,
        "wind_speed_ms": 5.0,
        "wave_height_m": 1.0,
        "water_depth_m": 60.0,
    }
    r1 = p.predict_fuel_with_uncertainty(point, coverage=0.90)
    r2 = p.predict_fuel_with_uncertainty(point, coverage=0.90)
    assert np.isclose(r1["fuel_prediction"], r2["fuel_prediction"], atol=1e-12)
    assert np.isclose(r1["uncertainty"]["lower_bound_kg_h"], r2["uncertainty"]["lower_bound_kg_h"], atol=1e-12)
    assert np.isclose(r1["uncertainty"]["upper_bound_kg_h"], r2["uncertainty"]["upper_bound_kg_h"], atol=1e-12)


def test_decision_record_hash_reproducibility():
    """Verify decision record canonicalization and SHA-256 hash reproduce bitwise identically."""
    from src.export.decision_exporter import build_optimization_decision_record, canonical_json_bytes, sha256_bytes
    sample_job = {
        "job_id": "OPT-repro001",
        "params": {"algorithm": "Hybrid_QI_A5", "seed": 1005, "budget": 2500, "weights": [0.35, 0.35, 0.3, 0, 0]},
        "result": {
            "feasible": True,
            "penalty_free": True,
            "penalty": 0.0,
            "soft_penalties": {},
            "objectives": {"fuel_t": 140.2, "opex_usd": 91200.0, "wtw_tco2e": 435.0, "delay_h": 0.0, "risk_cvar_excess": 0.0},
            "hard_violations": [],
            "vessels": [{"vessel_id": "CPS_Poseidon", "assigned_demand": "DEMAND_1", "speed_kn": 14.2, "fuel": "vlsfo", "shore_power": False}],
            "evaluations": 2500,
            "runtime_s": 1.15
        }
    }
    trace_id = "TRC-REPRO-FIXED"
    rec1 = build_optimization_decision_record("OPT-repro001", sample_job, operator_status="CONFIRMED", trace_id=trace_id)
    rec2 = build_optimization_decision_record("OPT-repro001", sample_job, operator_status="CONFIRMED", trace_id=trace_id)
    rec2["record_metadata"]["created_at_utc"] = rec1["record_metadata"]["created_at_utc"]
    rec2["decision"]["confirmation_timestamp_utc"] = rec1["decision"]["confirmation_timestamp_utc"]
    rec2["integrity"] = rec1["integrity"]

    b1 = canonical_json_bytes(rec1)
    b2 = canonical_json_bytes(rec2)
    assert b1 == b2
    assert sha256_bytes(b1) == sha256_bytes(b2)

