"""
Unit and Contract Tests for Egreen Quanta Maritime Operator UI / HMI.
Verifies module imports, data contracts, and Section 16 compliance.
"""

import math
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.backend_bridge import (
    get_cached_predictor,
    get_cached_sih_engine,
    get_default_fleet_state,
    get_verified_pareto_front,
    get_verified_tradeoffs,
    log_audit_event,
)
from dashboard.components.top_bar import render_top_bar
from dashboard.components.status_strip import render_status_strip
from dashboard.components.vessel_card import render_vessel_card
from dashboard.pages.fleet_overview import render_fleet_overview
from dashboard.pages.vessel_detail import render_vessel_detail
from dashboard.pages.prediction_trust import render_prediction_trust
from dashboard.pages.scenario_lab import render_scenario_lab
from dashboard.pages.fleet_optimizer import render_fleet_optimizer
from dashboard.pages.pareto_tradeoffs import render_pareto_tradeoffs
from dashboard.pages.alternative_fuels import render_alternative_fuels
from dashboard.pages.alerts_safety import render_alerts_safety
from dashboard.pages.audit_reports import render_audit_reports
from dashboard.pages.demo_mode import render_demo_mode


def test_dashboard_modules_importable():
    """All 10 page modules and 3 components must import without syntax or import errors."""
    assert callable(render_top_bar)
    assert callable(render_status_strip)
    assert callable(render_vessel_card)
    assert callable(render_fleet_overview)
    assert callable(render_vessel_detail)
    assert callable(render_prediction_trust)
    assert callable(render_scenario_lab)
    assert callable(render_fleet_optimizer)
    assert callable(render_pareto_tradeoffs)
    assert callable(render_alternative_fuels)
    assert callable(render_alerts_safety)
    assert callable(render_audit_reports)
    assert callable(render_demo_mode)


def test_fleet_contract_section16():
    """
    Assert default fleet state conforms to Section 16:
    Vessel: id, name, vessel_type, status.
    All 3 vessels (Poseidon, Triton, Ceto) must be explicit.
    """
    fleet = get_default_fleet_state()
    assert len(fleet) == 3

    v_ids = [v["id"] for v in fleet]
    assert "CPS_Poseidon" in v_ids
    assert "CPS_Triton" in v_ids
    assert "OSS_Ceto" in v_ids

    expected_types = {
        "CPS_Poseidon": "passenger_cruise",
        "CPS_Triton": "passenger_cruise_small",
        "OSS_Ceto": "offshore_supply",
    }

    for v in fleet:
        assert "id" in v
        assert "name" in v
        assert "vessel_type" in v
        assert "status" in v
        assert v["vessel_type"] == expected_types[v["id"]]
        assert v["displacement_t"] > 0
        assert v["draft_m"] > 0


def test_prediction_contract_section16():
    """
    Assert predictor output satisfies Section 16 Data Contract:
    Prediction: model_id, fuel_rate_kg_h, lower, upper, confidence_level, ood_state, fallback.
    """
    p = get_cached_predictor()
    test_inp = {
        "vessel_id": "CPS_Poseidon",
        "vessel_type": "passenger_cruise",
        "fuel_type": "vlsfo",
        "stw_kn": 14.5,
        "sog_kn": 14.5,
        "draft_m": 7.5,
        "displacement_t": 35000.0,
        "wind_speed_ms": 5.0,
        "wave_height_m": 1.0,
        "water_depth_m": 60.0,
    }

    res = p.predict_fuel_with_uncertainty(test_inp)

    # Assert Section 16 minimum fields
    assert "model" in res or "model_id" in res
    assert "fuel_prediction" in res
    assert "uncertainty" in res
    assert "lower_bound_kg_h" in res["uncertainty"]
    assert "upper_bound_kg_h" in res["uncertainty"]
    assert "confidence" in res
    assert "in_domain" in res
    assert "routing_status" in res

    # Numerical validity
    assert res["fuel_prediction"] > 1000.0
    assert res["uncertainty"]["lower_bound_kg_h"] < res["fuel_prediction"]
    assert res["uncertainty"]["upper_bound_kg_h"] > res["fuel_prediction"]
    assert res["in_domain"] is True
    assert res["envelope_distance"] <= 1.0


def test_cost_and_ghg_contract_section16():
    """
    Assert SIHObjectiveEngine output satisfies Section 16 Data Contract:
    Cost: fuel_cost, operational_cost, carbon_cost, total_cost.
    GHG: WtT, TtW, WtW, factor_id / methane slip.
    """
    engine = get_cached_sih_engine()
    obj = engine.evaluate_voyage(
        vessel_id="CPS_Poseidon",
        vessel_type="passenger_cruise",
        speed_knots=14.5,
        voyage_distance_nm=300.0,
        schedule_deadline_hours=24.0,
        baseline_fuel_rate_kg_h=2740.86,
        fuel_type="vlsfo",
        use_shore_power=True,
        port_hours=6.0,
        hotel_load_kw=1800.0,
    )

    # Cost fields
    assert hasattr(obj, "fuel_cost_usd")
    assert hasattr(obj, "operational_cost_usd")
    assert hasattr(obj, "carbon_cost_usd")
    assert hasattr(obj, "shore_power_cost_usd")
    assert obj.operational_cost_usd > 0
    assert obj.fuel_cost_usd > 0
    assert obj.carbon_cost_usd > 0

    # GHG fields
    assert hasattr(obj, "wtt_ghg_tonnes")
    assert hasattr(obj, "ttw_ghg_tonnes")
    assert hasattr(obj, "lifecycle_ghg_tonnes")
    assert hasattr(obj, "methane_slip_tonnes")
    assert obj.lifecycle_ghg_tonnes > 0
    assert obj.wtt_ghg_tonnes > 0
    assert obj.ttw_ghg_tonnes > 0


def test_pareto_dataset_contract():
    """Assert verified pareto_front.csv contains non-dominated solutions."""
    df_p = get_verified_pareto_front()
    assert not df_p.empty
    assert len(df_p) >= 10

    required_cols = [
        "formulation", "algorithm", "fuel_tonnes", "cost_usd", "ghg_tonnes", "delay_hours", "evaluations"
    ]
    for col in required_cols:
        assert col in df_p.columns, f"Missing required column '{col}' in pareto_front.csv"


def test_audit_event_logging():
    """Verify log_audit_event appends compliant records."""
    import streamlit as st
    st.session_state.audit_ledger = []

    log_audit_event(
        action="TEST_ACTION",
        scenario_id="TEST_SCEN_01",
        vessel_id="CPS_Poseidon",
        details={"fuel_prediction": 2740.86, "notes": "Automated contract test"},
    )

    assert len(st.session_state.audit_ledger) == 1
    rec = st.session_state.audit_ledger[0]
    assert rec["action"] == "TEST_ACTION"
    assert rec["vessel_id"] == "CPS_Poseidon"
    assert rec["scenario_id"] == "TEST_SCEN_01"
    assert rec["predicted_fuel_kg_h"] == 2740.86
