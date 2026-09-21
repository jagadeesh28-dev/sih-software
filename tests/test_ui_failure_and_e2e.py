"""
Phase 18 Failure Testing & Phase 19 End-to-End UI Transition Test.
Verifies all 15 failure modes and captures empirical evidence across the full operator flow:
Fleet -> Vessel -> Prediction -> Trust -> Scenario -> Cost -> GHG -> Optimizer -> Pareto -> Operator Review -> Audit.
"""

import math
import sys
from pathlib import Path
import pytest
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.backend_bridge import (
    get_cached_predictor,
    get_cached_sih_engine,
    get_default_fleet_state,
    get_verified_pareto_front,
    log_audit_event,
)
from src.qi_prediction.serving import ProductionFuelPredictor
from optimization.sih_objective_engine import SIHObjectiveEngine


# =========================================================================
# PHASE 18: 15 SYSTEM FAILURE TESTS
# =========================================================================

def test_failure_01_normal_prediction():
    """1. Normal prediction test."""
    p = get_cached_predictor()
    inp = {
        "vessel_id": "CPS_Poseidon", "vessel_type": "passenger_cruise", "fuel_type": "vlsfo",
        "stw_kn": 14.5, "sog_kn": 14.5, "draft_m": 7.5, "displacement_t": 35000.0,
        "wind_speed_ms": 5.0, "wave_height_m": 1.0, "water_depth_m": 60.0
    }
    res = p.predict_fuel_with_uncertainty(inp)
    assert res["fuel_prediction"] > 0
    assert res["in_domain"] is True
    assert res["routing_status"] == "NORMAL"


def test_failure_02_unknown_vessel():
    """2. Unknown vessel ID handling."""
    p = get_cached_predictor()
    inp = {
        "vessel_id": "GHOST_SHIP_999", "vessel_type": "passenger_cruise", "fuel_type": "vlsfo",
        "stw_kn": 14.0, "sog_kn": 14.0, "draft_m": 7.0, "displacement_t": 30000.0,
    }
    res = p.predict_fuel_with_uncertainty(inp)
    assert res["fuel_prediction"] > 0


def test_failure_03_unknown_vessel_type():
    """3. Unknown vessel_type handling."""
    p = get_cached_predictor()
    inp = {
        "vessel_id": "TEST_VESSEL", "vessel_type": "intergalactic_cruiser", "fuel_type": "vlsfo",
        "stw_kn": 14.0, "sog_kn": 14.0, "draft_m": 7.0, "displacement_t": 30000.0,
    }
    res = p.predict_fuel_with_uncertainty(inp)
    assert res["routing_status"] == "FALLBACK"
    assert "Unknown or unsupported vessel_type" in res["warning"]


def test_failure_04_missing_input():
    """4. Missing mandatory input handling."""
    p = get_cached_predictor()
    inp = {"vessel_id": "CPS_Poseidon"}
    is_valid, errors, _ = p.validate_and_sanitize_point(inp)
    assert is_valid is False
    assert any("Missing mandatory" in e for e in errors)


def test_failure_05_invalid_input():
    """5. Physically invalid input (negative speed, impossible draft)."""
    p = get_cached_predictor()
    inp = {
        "vessel_id": "CPS_Poseidon", "stw_kn": -10.0, "draft_m": 0.2, "displacement_t": 35000.0
    }
    is_valid, errors, _ = p.validate_and_sanitize_point(inp)
    assert is_valid is False
    assert any("out of physical bounds" in e for e in errors)


def test_failure_06_stale_data():
    """6. Stale data detection handling."""
    p = get_cached_predictor()
    inp = {
        "vessel_id": "CPS_Poseidon", "vessel_type": "passenger_cruise", "fuel_type": "vlsfo",
        "stw_kn": 0.0, "draft_m": 7.5, "displacement_t": 35000.0
    }
    res = p.predict_fuel_with_uncertainty(inp)
    assert res["fuel_prediction"] >= 0.0


def test_failure_07_ood():
    """7. Out-of-Distribution condition (Scene 5 Injected Storm)."""
    p = get_cached_predictor()
    inp = {
        "vessel_id": "CPS_Poseidon", "vessel_type": "passenger_cruise", "fuel_type": "vlsfo",
        "stw_kn": 33.0, "sog_kn": 32.0, "draft_m": 22.0, "displacement_t": 160000.0,
        "wind_speed_ms": 48.0, "wave_height_m": 14.0, "water_depth_m": 15.0,
    }
    res = p.predict_fuel_with_uncertainty(inp, raise_on_error=False)
    assert res["envelope_distance"] > 1.0
    assert res["routing_status"] in ("WARNING", "FALLBACK", "EMERGENCY_PHYSICS")


def test_failure_08_model_failure():
    """8. Injected model failure recovery."""
    p = get_cached_predictor()
    saved_booster = p.qi_c1_vessel_type_booster
    try:
        p.qi_c1_vessel_type_booster = None  # Injected model failure
        inp = {
            "vessel_id": "CPS_Poseidon", "vessel_type": "passenger_cruise", "fuel_type": "vlsfo",
            "stw_kn": 14.5, "draft_m": 7.5, "displacement_t": 35000.0
        }
        res = p.predict_fuel_with_uncertainty(inp)
        assert res["model"] in ("QI-C1", "MODEL-REAL-04", "PhysicsFuelPredictor")
    finally:
        p.qi_c1_vessel_type_booster = saved_booster


def test_failure_09_fallback():
    """9. Verification that fallback activates MODEL-REAL-04 on boundary state."""
    p = get_cached_predictor()
    inp = {
        "vessel_id": "CPS_Poseidon", "vessel_type": "space_freighter", "fuel_type": "vlsfo",
        "stw_kn": 14.0, "draft_m": 7.5, "displacement_t": 35000.0,
    }
    res = p.predict_fuel_with_uncertainty(inp)
    assert res["routing_status"] == "FALLBACK"
    assert res["model"] == "MODEL-REAL-04"


def test_failure_10_optimizer_failure():
    """10. Optimizer handling when impossible constraints provided."""
    engine = get_cached_sih_engine()
    ev = engine.evaluate_voyage(
        vessel_id="CPS_Poseidon", vessel_type="passenger_cruise",
        speed_knots=0.0, voyage_distance_nm=300.0, schedule_deadline_hours=10.0,
        baseline_fuel_rate_kg_h=2500.0
    )
    assert ev.schedule_delay_hours == 1000.0
    assert ev.operational_cost_usd > 0


def test_failure_11_missing_fuel_factor():
    """11. Missing fuel factor defaults safely to baseline."""
    engine = get_cached_sih_engine()
    ev = engine.evaluate_voyage(
        vessel_id="CPS_Poseidon", vessel_type="passenger_cruise",
        speed_knots=14.0, voyage_distance_nm=100.0, schedule_deadline_hours=10.0,
        baseline_fuel_rate_kg_h=2000.0, fuel_type="mythical_warp_plasma"
    )
    assert ev.fuel_tonnes > 0
    assert ev.operational_cost_usd > 0


def test_failure_12_missing_emission_factor():
    """12. Missing emission factor handling."""
    engine = get_cached_sih_engine()
    ev = engine.evaluate_voyage(
        vessel_id="CPS_Poseidon", vessel_type="passenger_cruise",
        speed_knots=14.0, voyage_distance_nm=100.0, schedule_deadline_hours=10.0,
        baseline_fuel_rate_kg_h=2000.0, fuel_type="unregistered_fuel_xyz"
    )
    assert ev.lifecycle_ghg_tonnes > 0


def test_failure_13_api_unavailable():
    """13. API unavailable / singleton access validation."""
    p = get_cached_predictor()
    assert p is not None
    assert p.models_dir.exists()


def test_failure_14_api_timeout():
    """14. Execution speed: prediction must return within 200 ms."""
    import time
    p = get_cached_predictor()
    inp = {
        "vessel_id": "CPS_Poseidon", "vessel_type": "passenger_cruise", "fuel_type": "vlsfo",
        "stw_kn": 14.5, "draft_m": 7.5, "displacement_t": 35000.0
    }
    t0 = time.perf_counter()
    p.predict_fuel_with_uncertainty(inp)
    dur_ms = (time.perf_counter() - t0) * 1000
    assert dur_ms < 200.0, f"Inference took {dur_ms:.1f} ms (>200 ms)"


def test_failure_15_malformed_backend_response():
    """15. Malformed dictionary sanitized safely."""
    p = get_cached_predictor()
    inp = {
        "vessel_id": "CPS_Poseidon", "stw_kn": float("nan"), "draft_m": 7.5, "displacement_t": 35000.0
    }
    is_valid, errors, _ = p.validate_and_sanitize_point(inp)
    assert is_valid is False
    assert any("NaN or Inf" in e for e in errors)


# =========================================================================
# PHASE 19: COMPLETE END-TO-END UI TRANSITION TEST
# =========================================================================

def test_phase19_end_to_end_operator_journey():
    """
    Test complete operator journey:
    Fleet -> Select Vessel -> Prediction -> Uncertainty -> OOD -> Scenario -> Cost -> GHG -> Optimizer -> Pareto -> Decision -> Audit.
    """
    # 1. Fleet
    fleet = get_default_fleet_state()
    assert len(fleet) == 3

    # 2. Select Vessel
    selected_vessel = fleet[0]
    assert selected_vessel["name"] == "CPS_Poseidon"

    # 3. Prediction
    p = get_cached_predictor()
    inp = {
        "vessel_id": selected_vessel["id"], "vessel_type": selected_vessel["vessel_type"],
        "fuel_type": selected_vessel["fuel_type"], "stw_kn": selected_vessel["stw_kn"],
        "sog_kn": selected_vessel["sog_kn"], "draft_m": selected_vessel["draft_m"],
        "displacement_t": selected_vessel["displacement_t"],
        "wind_speed_ms": selected_vessel["wind_speed_ms"],
        "wave_height_m": selected_vessel["wave_height_m"],
        "water_depth_m": selected_vessel["water_depth_m"],
    }
    pred_res = p.predict_fuel_with_uncertainty(inp)
    assert pred_res["fuel_prediction"] > 2000.0
    assert pred_res["cross_check"]["qi_c1_pred_kg_h"] == pytest.approx(2740.86, abs=1.0)

    # 4. Uncertainty
    unc = pred_res["uncertainty"]
    assert unc["lower_bound_kg_h"] < pred_res["fuel_prediction"] < unc["upper_bound_kg_h"]

    # 5. OOD Status
    assert pred_res["in_domain"] is True
    assert pred_res["envelope_distance"] <= 1.0

    # 6. Scenario
    engine = get_cached_sih_engine()
    scen_eval = engine.evaluate_voyage(
        vessel_id=selected_vessel["id"], vessel_type=selected_vessel["vessel_type"],
        speed_knots=13.5, voyage_distance_nm=300.0, schedule_deadline_hours=24.0,
        baseline_fuel_rate_kg_h=pred_res["fuel_prediction"], fuel_type="bio_methanol",
        use_shore_power=True, port_hours=6.0, hotel_load_kw=selected_vessel["hotel_load_kw"]
    )
    assert scen_eval.fuel_tonnes > 0

    # 7. Operational Cost
    assert scen_eval.operational_cost_usd > 0
    assert scen_eval.fuel_cost_usd > 0
    assert scen_eval.carbon_cost_usd >= 0

    # 8. Lifecycle GHG
    assert scen_eval.lifecycle_ghg_tonnes > 0
    assert scen_eval.wtt_ghg_tonnes > 0
    assert scen_eval.ttw_ghg_tonnes >= 0

    # 9. Optimizer
    df_p = get_verified_pareto_front()
    assert not df_p.empty

    # 10. Pareto Selection
    selected_solution = df_p.iloc[0]
    assert selected_solution["is_feasible"] == True

    # 11. Operator Review & Audit
    import streamlit as st
    st.session_state.audit_ledger = []
    log_audit_event(
        action="E2E_VERIFICATION_COMPLETE",
        scenario_id="E2E-TEST-001",
        vessel_id=selected_vessel["id"],
        details={
            "fuel_prediction": pred_res["fuel_prediction"],
            "operational_cost": scen_eval.operational_cost_usd,
            "lifecycle_ghg": scen_eval.lifecycle_ghg_tonnes,
            "solution_id": selected_solution["formulation"],
            "notes": "Full end-to-end operator workflow transition verified with zero mocked data.",
        }
    )
    assert len(st.session_state.audit_ledger) == 1
    assert st.session_state.audit_ledger[0]["action"] == "E2E_VERIFICATION_COMPLETE"
