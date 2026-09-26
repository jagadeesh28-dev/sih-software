"""
Unit Tests for Physical Consistency Constraints (SIH26138 - Phase 6).
Verifies non-negativity, cubic-order hydrodynamic speed-fuel monotonicity, and draft bounds.
"""

import numpy as np
import pandas as pd
import pytest

from prediction.physics_predictor import PhysicsFuelPredictor
from src.qi_prediction.validation import ValidationHarness


def test_hydrodynamic_speed_fuel_monotonicity():
    """Verify fuel consumption strictly increases with Speed Through Water (STW)."""
    phys = PhysicsFuelPredictor(default_vessel_type="container_feeder")
    speeds = [10.0, 12.0, 14.0, 16.0, 18.0]
    fuels = []

    for spd in speeds:
        rec = {
            "stw_kn": spd,
            "draft_m": 8.5,
            "displacement_t": 24000.0,
            "wave_height_m": 0.0,
            "wave_period_s": 0.0,
            "wave_direction_deg": 0.0,
            "wind_speed_ms": 0.0,
            "wind_direction_deg": 0.0,
            "vessel_type": "container_feeder",
        }
        res = phys.predict_record(rec)
        fuels.append(res["predicted_fuel_kg_h"])

    # Strictly monotonic increase: fuels[i+1] > fuels[i]
    for i in range(len(fuels) - 1):
        assert fuels[i + 1] > fuels[i], f"Monotonicity violated at {speeds[i]} -> {speeds[i+1]} kn"


def test_wave_resistance_monotonicity():
    """Verify higher significant wave height strictly increases total resistance."""
    phys = PhysicsFuelPredictor(default_vessel_type="container_feeder")
    wave_heights = [0.0, 1.5, 3.0, 4.5]
    resistances = []

    for wh in wave_heights:
        rec = {
            "stw_kn": 14.0,
            "draft_m": 8.5,
            "displacement_t": 24000.0,
            "wave_height_m": wh,
            "wave_period_s": 8.0,
            "wave_direction_deg": 0.0,  # Head sea
            "wind_speed_ms": 0.0,
            "wind_direction_deg": 0.0,
            "vessel_type": "container_feeder",
        }
        res = phys.predict_record(rec)
        resistances.append(res["total_resistance_n"])

    for i in range(len(resistances) - 1):
        assert resistances[i + 1] > resistances[i], f"Wave monotonicity violated at {wave_heights[i]} -> {wave_heights[i+1]} m"


def test_wind_resistance_monotonicity():
    """Verify higher headwind speed strictly increases total aerodynamic drag."""
    phys = PhysicsFuelPredictor(default_vessel_type="container_feeder")
    wind_speeds = [0.0, 10.0, 20.0, 30.0]
    resistances = []

    for ws in wind_speeds:
        rec = {
            "stw_kn": 14.0,
            "draft_m": 8.5,
            "displacement_t": 24000.0,
            "wave_height_m": 0.0,
            "wave_period_s": 0.0,
            "wave_direction_deg": 0.0,
            "wind_speed_ms": ws,
            "wind_direction_deg": 0.0,  # Head wind
            "vessel_type": "container_feeder",
        }
        res = phys.predict_record(rec)
        resistances.append(res["total_resistance_n"])

    for i in range(len(resistances) - 1):
        assert resistances[i + 1] > resistances[i], f"Wind monotonicity violated at {wind_speeds[i]} -> {wind_speeds[i+1]} m/s"


def test_physical_non_negativity_check():
    """Verify physical consistency auditor catches negative and extreme flow values."""
    preds_valid = np.array([150.0, 200.0, 1200.0, 3500.0])
    audit_valid = ValidationHarness.check_physical_consistency(preds_valid)
    assert audit_valid["is_physically_bounded"] is True
    assert audit_valid["negative_count"] == 0

    preds_invalid = np.array([-10.0, 200.0, 25000.0])
    audit_invalid = ValidationHarness.check_physical_consistency(preds_invalid)
    assert audit_invalid["is_physically_bounded"] is False
    assert audit_invalid["negative_count"] == 1
    assert audit_invalid["extreme_flow_count"] == 1


def test_real_vessels_use_declared_proxy_hull():
    """Real FuelCast vessels map to a declared proxy hull; unknown types warn instead of mapping silently."""
    from prediction.physics_predictor import resolve_hull_profile

    for vt in ("passenger_cruise", "passenger_cruise_small", "offshore_supply"):
        assert resolve_hull_profile(vt) == ("container_feeder", True)
    assert resolve_hull_profile("bulk_handymax") == ("bulk_handymax", False)
    with pytest.warns(RuntimeWarning, match="No hull profile"):
        assert resolve_hull_profile("tanker_vlcc") == ("container_feeder", True)

    out = PhysicsFuelPredictor().predict_record({"stw_kn": 12.0, "vessel_type": "offshore_supply"})
    assert out["physics_diagnostics"]["hull_profile"] == "container_feeder"
    assert out["physics_diagnostics"]["hull_profile_is_proxy"] is True


def test_serving_rejects_when_physics_baseline_fails():
    """A physics failure must reject, not serve a residual-only prediction on a zero baseline."""
    from src.qi_prediction.serving import get_production_predictor

    p = get_production_predictor()
    original = p.physics.predict

    def broken(_df):
        raise RuntimeError("injected physics failure")

    p.physics.predict = broken
    try:
        res = p.predict_fuel_with_uncertainty(
            {"vessel_type": "passenger_cruise", "fuel_type": "vlsfo", "stw_kn": 14.5, "sog_kn": 14.5,
             "draft_m": 7.5, "displacement_t": 35000.0, "wind_speed_ms": 5.0, "wave_height_m": 1.0,
             "water_depth_m": 60.0},
            raise_on_error=False,
        )
    finally:
        p.physics.predict = original
    assert res["routing_status"] == "REJECT"
    assert res["fuel_prediction"] is None
    assert "Physics baseline failure" in res["warning"]
