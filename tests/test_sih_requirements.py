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
from optimization.canonical_mapper import canonicalize_vessel_type, canonicalize_fuel_type, is_supported_fuel_type
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
    res = p.predict_fuel_with_uncertainty(raw_input, raise_on_error=False)
    assert res["routing_status"] == "REJECT" and res["fuel_prediction"] is None
    assert "Unsupported vessel_type" in res["warning"]
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


# -----------------------------------------------------------------------------
# 5. FUEL TYPE RECOGNITION & SAFETY CONTRACT TESTS (PHASE 8 HARDENING)
# -----------------------------------------------------------------------------

def test_fuel_type_canonical_recognition():
    """Verify supported fuels and aliases are canonically recognized."""
    # Standard fuels
    assert is_supported_fuel_type("vlsfo") is True
    assert is_supported_fuel_type("mgo") is True
    assert is_supported_fuel_type("bio_methanol") is True
    assert is_supported_fuel_type("fossil_lng") is True
    assert is_supported_fuel_type("green_ammonia") is True
    assert is_supported_fuel_type("liquid_hydrogen") is True

    # Aliases
    assert is_supported_fuel_type("lng") is True
    assert is_supported_fuel_type("methanol") is True
    assert is_supported_fuel_type("ammonia") is True
    assert is_supported_fuel_type("hydrogen") is True
    assert is_supported_fuel_type("marine_gas_oil") is True

    # Canonical mapping
    assert canonicalize_fuel_type("lng") == "fossil_lng"
    assert canonicalize_fuel_type("methanol") == "bio_methanol"

    # Unsupported fuels
    assert is_supported_fuel_type("plutonium_239") is False
    assert is_supported_fuel_type("uranium") is False
    assert is_supported_fuel_type("heavy_crude") is False
    assert is_supported_fuel_type(None) is False
    assert is_supported_fuel_type(12345) is False


def test_fuel_type_serving_safety_contract_tests_a_through_i():
    """
    Verify serving engine safety contract for supported and unsupported fuels.
    Tests:
    A: Supported fuel vlsfo -> fuel_warning is None, routing NORMAL
    B: Supported fuel fossil_lng -> fuel_warning is None
    C: Supported fuel bio_methanol -> fuel_warning is None
    D: Supported fuel green_ammonia -> fuel_warning is None
    E: Supported fuel liquid_hydrogen -> fuel_warning is None
    F: Supported alias lng -> fuel_warning is None
    G: Unsupported fuel plutonium_239 -> fuel_warning populated, LOW confidence, FALLBACK routing
    H: Missing/omitted fuel -> fuel_warning is None (safe default)
    I: Corrupted non-string fuel -> fuel_warning populated, safe fallback
    """
    from src.qi_prediction.serving import get_production_predictor
    p = get_production_predictor()

    base_input = {
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

    # Test A: Supported fuel vlsfo
    inp_a = dict(base_input, fuel_type="vlsfo")
    res_a = p.predict_fuel_with_uncertainty(inp_a)
    assert res_a.get("fuel_warning") is None
    assert res_a.get("routing_status") == "NORMAL"

    # Test B: Supported fuel fossil_lng
    inp_b = dict(base_input, fuel_type="fossil_lng")
    res_b = p.predict_fuel_with_uncertainty(inp_b)
    assert res_b.get("fuel_warning") is None

    # Test C: Supported fuel bio_methanol
    inp_c = dict(base_input, fuel_type="bio_methanol")
    res_c = p.predict_fuel_with_uncertainty(inp_c)
    assert res_c.get("fuel_warning") is None

    # Test D: Supported fuel green_ammonia
    inp_d = dict(base_input, fuel_type="green_ammonia")
    res_d = p.predict_fuel_with_uncertainty(inp_d)
    assert res_d.get("fuel_warning") is None

    # Test E: Supported fuel liquid_hydrogen
    inp_e = dict(base_input, fuel_type="liquid_hydrogen")
    res_e = p.predict_fuel_with_uncertainty(inp_e)
    assert res_e.get("fuel_warning") is None

    # Test F: Supported alias lng
    inp_f = dict(base_input, fuel_type="lng")
    res_f = p.predict_fuel_with_uncertainty(inp_f)
    assert res_f.get("fuel_warning") is None

    # Test G: Unsupported fuel plutonium_239
    inp_g = dict(base_input, fuel_type="plutonium_239")
    res_g = p.predict_fuel_with_uncertainty(inp_g)
    warn_g = res_g.get("fuel_warning")
    assert warn_g is not None, "Expected fuel_warning to be populated for unsupported fuel"
    assert warn_g["code"] == "UNSUPPORTED_FUEL_TYPE"
    assert warn_g["requested"] == "plutonium_239"
    assert warn_g["applied"] == "vlsfo"
    assert "Unsupported fuel_type" in warn_g["message"]
    assert res_g["confidence"] == "LOW"
    assert res_g["routing_status"] == "FALLBACK"
    assert res_g["model"] == "MODEL-REAL-04"
    assert "Unsupported fuel_type" in res_g.get("warning", "")

    # Test H: Missing/omitted fuel (safe default without warning)
    inp_h = dict(base_input)  # fuel_type omitted
    res_h = p.predict_fuel_with_uncertainty(inp_h)
    assert res_h.get("fuel_warning") is None

    # Test I: Corrupted non-string fuel
    inp_i = dict(base_input, fuel_type=12345)
    res_i = p.predict_fuel_with_uncertainty(inp_i)
    warn_i = res_i.get("fuel_warning")
    assert warn_i is not None
    assert warn_i["code"] == "UNSUPPORTED_FUEL_TYPE"
    assert res_i["confidence"] == "LOW"
    assert res_i["routing_status"] == "FALLBACK"

