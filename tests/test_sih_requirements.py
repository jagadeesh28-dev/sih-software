"""
SIH26138 — Egreen Quanta: Core Requirements Verification Tests.
Tests:
1. Explicit vessel_type recognition and categorical handling
2. Unknown/corrupted vessel_type safety fallback
3. Operational cost formulation & price sensitivities
4. Lifecycle GHG accounting & emission factor sensitivity
5. Shore power electricity cost & connection fee
6. Multi-objective Pareto dominance & trade-off consistency
7. Deterministic evaluation reproducibility
"""

import math
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from optimization.sih_objective_engine import SIHObjectiveEngine, SIHOptimizationObjectives
from optimization.canonical_mapper import canonicalize_vessel_type, canonicalize_fuel_type
from lca.fuel_registry import FuelPathwayRegistry


@pytest.fixture
def sih_engine():
    return SIHObjectiveEngine()


# -----------------------------------------------------------------------------
# 1. VESSEL TYPE FEATURE TESTS
# -----------------------------------------------------------------------------

def test_vessel_type_canonical_recognition():
    """Verify standard FuelCast vessels map to certified naval architectural classes."""
    assert canonicalize_vessel_type("passenger_cruise") == "passenger_cruise"
    assert canonicalize_vessel_type("passenger_cruise_small") == "passenger_cruise_small"
    assert canonicalize_vessel_type("offshore_supply") == "offshore_supply"

    # Alias recognition
    assert canonicalize_vessel_type("cruise_passenger") == "passenger_cruise"
    assert canonicalize_vessel_type("small_cruise") == "passenger_cruise_small"
    assert canonicalize_vessel_type("osv") == "offshore_supply"


def test_vessel_type_unknown_handling():
    """Verify unknown vessel type triggers domain guard fallback and warning in serving engine."""
    from src.qi_prediction.serving import get_production_predictor
    p = get_production_predictor()
    raw_input = {
        "vessel_id": "Unknown_Craft",
        "vessel_type": "nuclear_submarine",
        "fuel_type": "vlsfo",
        "stw_kn": 14.5,
        "sog_kn": 14.5,
        "draft_m": 7.5,
        "displacement_t": 35000.0,
        "wind_speed_ms": 5.0,
        "wave_height_m": 1.0,
        "water_depth_m": 60.0,
    }
    res = p.predict_fuel_with_uncertainty(raw_input)
    assert res["routing_status"] == "FALLBACK"
    assert "nuclear_submarine" in res["warning"]
    assert res["confidence"] in ("LOW", "MEDIUM")


# -----------------------------------------------------------------------------
# 2. OPERATIONAL COST TESTS
# -----------------------------------------------------------------------------

def test_operational_cost_formulation(sih_engine):
    """
    Verify exact cost breakdown: C_total = C_fuel + C_carbon + C_OPS + C_schedule + C_fueleu.
    Ensure zero double counting.
    """
    res = sih_engine.evaluate_voyage(
        vessel_id="CPS_Poseidon",
        vessel_type="passenger_cruise",
        speed_knots=15.0,
        voyage_distance_nm=150.0,
        schedule_deadline_hours=12.0,  # Voyage takes 10h -> 0 delay
        baseline_fuel_rate_kg_h=2500.0,
        fuel_type="vlsfo",
        use_shore_power=True,
        port_hours=5.0,
        hotel_load_kw=1000.0,
    )

    # Voyage time = 150 / 15 = 10 hours
    # Fuel = 2500 * 10 = 25,000 kg = 25.0 tonnes
    assert math.isclose(res.fuel_tonnes, 25.0, rel_tol=1e-3)
    assert res.schedule_delay_hours == 0.0

    # Fuel cost = 25.0 tonnes * $620/tonne = $15,500
    assert math.isclose(res.fuel_cost_usd, 25.0 * 620.0, rel_tol=1e-2)

    # Shore power cost = (1000 kW * 5h * $0.18/kWh) + $500 fee = $900 + $500 = $1,400
    assert math.isclose(res.shore_power_cost_usd, 1400.0, rel_tol=1e-2)

    # Schedule penalty = $0
    assert res.schedule_penalty_usd == 0.0

    # Total opex must strictly equal sum of subcomponents
    expected_sum = (
        res.fuel_cost_usd
        + res.carbon_cost_usd
        + res.shore_power_cost_usd
        + res.schedule_penalty_usd
        + res.fueleu_penalty_usd
    )
    assert math.isclose(res.operational_cost_usd, expected_sum, abs_tol=0.1)


def test_fuel_price_sensitivity():
    """Verify operational cost adjusts linearly when bunker price changes."""
    engine_base = SIHObjectiveEngine(bunker_price_overrides={"vlsfo": 600.0})
    engine_surge = SIHObjectiveEngine(bunker_price_overrides={"vlsfo": 900.0})

    kwargs = dict(
        vessel_id="CPS_Poseidon",
        vessel_type="passenger_cruise",
        speed_knots=15.0,
        voyage_distance_nm=150.0,
        schedule_deadline_hours=15.0,
        baseline_fuel_rate_kg_h=2000.0,
        fuel_type="vlsfo",
    )

    res_base = engine_base.evaluate_voyage(**kwargs)
    res_surge = engine_surge.evaluate_voyage(**kwargs)

    # Delta must exactly equal fuel_mass * (900 - 600)
    expected_delta = res_base.fuel_tonnes * 300.0
    actual_delta = res_surge.fuel_cost_usd - res_base.fuel_cost_usd
    assert math.isclose(actual_delta, expected_delta, rel_tol=1e-2)


def test_carbon_price_sensitivity():
    """Verify carbon allowance cost scales linearly with carbon tax."""
    engine_c90 = SIHObjectiveEngine(carbon_price_usd_tonne=90.0)
    engine_c180 = SIHObjectiveEngine(carbon_price_usd_tonne=180.0)

    kwargs = dict(
        vessel_id="CPS_Poseidon",
        vessel_type="passenger_cruise",
        speed_knots=15.0,
        voyage_distance_nm=150.0,
        schedule_deadline_hours=15.0,
        baseline_fuel_rate_kg_h=2000.0,
        fuel_type="vlsfo",
    )

    res_90 = engine_c90.evaluate_voyage(**kwargs)
    res_180 = engine_c180.evaluate_voyage(**kwargs)

    assert math.isclose(res_180.carbon_cost_usd, 2.0 * res_90.carbon_cost_usd, rel_tol=1e-2)


# -----------------------------------------------------------------------------
# 3. LIFECYCLE GHG ACCOUNTING TESTS
# -----------------------------------------------------------------------------

def test_lifecycle_ghg_accounting(sih_engine):
    """Verify strict separation of Well-to-Tank and Tank-to-Wake emissions."""
    res = sih_engine.evaluate_voyage(
        vessel_id="CPS_Poseidon",
        vessel_type="passenger_cruise",
        speed_knots=15.0,
        voyage_distance_nm=150.0,
        schedule_deadline_hours=15.0,
        baseline_fuel_rate_kg_h=2000.0,
        fuel_type="vlsfo",
    )

    # WtW GHG must be strictly positive and exceed TtW direct combustion
    assert res.lifecycle_ghg_tonnes > 0.0
    assert res.wtt_ghg_tonnes > 0.0
    assert res.ttw_ghg_tonnes > 0.0
    assert res.lifecycle_ghg_tonnes > res.ttw_ghg_tonnes


def test_alternative_fuel_ghg_reduction(sih_engine):
    """Verify bio-methanol exhibits lower net lifecycle GHG than fossil VLSFO under invariant work."""
    kwargs = dict(
        vessel_id="CPS_Poseidon",
        vessel_type="passenger_cruise",
        speed_knots=15.0,
        voyage_distance_nm=150.0,
        schedule_deadline_hours=15.0,
        baseline_fuel_rate_kg_h=2500.0,
    )
    res_vlsfo = sih_engine.evaluate_voyage(fuel_type="vlsfo", **kwargs)
    res_methanol = sih_engine.evaluate_voyage(fuel_type="bio_methanol", **kwargs)

    # Bio-methanol has climate-neutral biogenic combustion (lower net WtW)
    assert res_methanol.lifecycle_ghg_tonnes < res_vlsfo.lifecycle_ghg_tonnes


# -----------------------------------------------------------------------------
# 4. PARETO DOMINANCE & TRADE-OFF TESTS
# -----------------------------------------------------------------------------

def test_pareto_dominance_logic():
    """Verify multi-objective non-dominated sorting."""
    # 4 points: [Fuel, Cost]
    # Point 0: [10, 1000] - non-dominated
    # Point 1: [8, 1200]  - non-dominated
    # Point 2: [12, 1500] - dominated by both
    # Point 3: [6, 1800]  - non-dominated
    costs = np.array([
        [10.0, 1000.0],
        [8.0, 1200.0],
        [12.0, 1500.0],
        [6.0, 1800.0],
    ])
    efficient = SIHObjectiveEngine.is_pareto_efficient(costs)
    assert np.array_equal(efficient, np.array([True, True, False, True]))


def test_deterministic_evaluation(sih_engine):
    """Verify that evaluate_voyage is strictly deterministic."""
    kwargs = dict(
        vessel_id="OSS_Ceto",
        vessel_type="offshore_supply",
        speed_knots=12.0,
        voyage_distance_nm=100.0,
        schedule_deadline_hours=10.0,
        baseline_fuel_rate_kg_h=600.0,
        fuel_type="mgo",
    )
    r1 = sih_engine.evaluate_voyage(**kwargs)
    r2 = sih_engine.evaluate_voyage(**kwargs)

    assert r1.fuel_tonnes == r2.fuel_tonnes
    assert r1.operational_cost_usd == r2.operational_cost_usd
    assert r1.lifecycle_ghg_tonnes == r2.lifecycle_ghg_tonnes
