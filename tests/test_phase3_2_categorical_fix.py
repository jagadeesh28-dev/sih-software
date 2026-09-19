"""
Unit & Regression Tests for Phase 3.2 Category Normalization & Feasibility Restoration.
Validates:
1. Canonical vessel category accepted.
2. Noncanonical alias handled correctly.
3. Valid candidate is IN_DOMAIN.
4. Valid candidate is feasible.
5. Invalid category is rejected.
6. SafeFuelObjective still blocks extrapolation.
7. CII unavailable-data state does not create artificial penalty.
8. Genuine regulatory violation still generates penalty.
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from optimization.canonical_mapper import (
    canonicalize_vessel_type,
    canonicalize_fuel_type,
    get_baseline_fuel_for_vessel,
    CANONICAL_VESSEL_TYPES,
    CANONICAL_FUEL_TYPES,
)
from prediction.domain_checker import DomainChecker
from prediction.safe_objective import SafeFuelObjective
from prediction.ml_baseline import PureMLPredictor
from prediction.physics_predictor import PhysicsFuelPredictor
from prediction.quantile_model import QuantileUncertaintyPredictor
from optimization.regulatory import FleetRegulatoryEngine
from optimization.constraints import FleetConstraintManager
from optimization.evaluator import FleetEvaluationEngine
from optimization.variables import SolutionChromosome, VesselAssignmentDecision
from experiments.exp_phase3_master_runner import load_real_surrogates, BENCHMARK_SCENARIOS


def test_canonical_mapper_vocabulary():
    """Verify canonical vocabularies and alias resolution."""
    assert "passenger_cruise" in CANONICAL_VESSEL_TYPES
    assert "offshore_supply" in CANONICAL_VESSEL_TYPES
    assert "cargo_feeder" in CANONICAL_VESSEL_TYPES

    # Aliases
    assert canonicalize_vessel_type("cruise_passenger") == "passenger_cruise"
    assert canonicalize_vessel_type("cruise") == "passenger_cruise"
    assert canonicalize_vessel_type("osv") == "offshore_supply"
    assert canonicalize_vessel_type("container") == "cargo_feeder"
    assert canonicalize_vessel_type("passenger_cruise") == "passenger_cruise"

    # Fuels
    assert canonicalize_fuel_type("vlsfo") == "vlsfo"
    assert canonicalize_fuel_type("biomethanol") == "bio_methanol"
    assert canonicalize_fuel_type("methanol") == "bio_methanol"


def test_domain_checker_accepts_canonical_and_alias():
    """Verify DomainChecker fits canonical categories and resolves aliases seamlessly."""
    # Synthetic training sample mimicking Poseidon telemetry
    n = 200
    train_df = pd.DataFrame({
        "stw_kn": np.random.uniform(10.0, 20.0, n),
        "sog_kn": np.random.uniform(10.0, 20.0, n),
        "draft_m": np.full(n, 7.5),
        "displacement_t": np.full(n, 42000.0),
        "wind_speed_ms": np.random.uniform(2.0, 15.0, n),
        "wind_direction_deg": np.random.uniform(0.0, 360.0, n),
        "wave_height_m": np.random.uniform(0.5, 3.0, n),
        "wave_period_s": np.random.uniform(4.0, 10.0, n),
        "wave_direction_deg": np.random.uniform(0.0, 360.0, n),
        "current_speed_ms": np.random.uniform(0.1, 1.0, n),
        "current_direction_deg": np.random.uniform(0.0, 360.0, n),
        "water_depth_m": np.random.uniform(50.0, 500.0, n),
        "vessel_type": ["passenger_cruise"] * n,
        "fuel_type": ["vlsfo"] * n,
    })

    dc = DomainChecker(feature_cols=list(train_df.columns)).fit(train_df)
    assert "passenger_cruise" in dc.valid_categories["vessel_type"]

    # 1. Point with canonical category
    pt_canon = {c: float(train_df[c].iloc[0]) if c not in ["vessel_type", "fuel_type"] else train_df[c].iloc[0] for c in train_df.columns}
    res_canon = dc.evaluate_point(pt_canon)
    assert res_canon["domain_status"] in ["IN_DOMAIN", "NEAR_BOUNDARY"]
    assert res_canon["is_valid_candidate"] is True

    # 2. Point with historical alias "cruise_passenger"
    pt_alias = dict(pt_canon)
    pt_alias["vessel_type"] = "cruise_passenger"
    res_alias = dc.evaluate_point(pt_alias)
    assert res_alias["domain_status"] in ["IN_DOMAIN", "NEAR_BOUNDARY"]
    assert res_alias["is_valid_candidate"] is True

    # 3. Point with bogus/unknown category
    pt_bogus = dict(pt_canon)
    pt_bogus["vessel_type"] = "submarine"
    res_bogus = dc.evaluate_point(pt_bogus)
    assert res_bogus["domain_status"] == "OUT_OF_DOMAIN"
    assert res_bogus["is_valid_candidate"] is False
    assert any("Unknown category vessel_type" in r for r in res_bogus["reasons"])


def test_cii_baseline_single_voyage_vs_annual():
    """Verify single-voyage leg produces NOT_EVALUABLE with no artificial penalty."""
    reg = FleetRegulatoryEngine()
    cm = FleetConstraintManager()

    # Single voyage leg evaluation (annual_context=False)
    res_voyage = reg.evaluate_imo_cii(
        vessel_class="passenger_cruise",
        capacity_val=70000.0,
        co2_emissions_tonnes=150.0,
        distance_nm=450.0,
        annual_context=False,
    )
    assert res_voyage["rating"] == "NOT_EVALUABLE"
    assert res_voyage["status"] == "VOYAGE_INDICATOR_ONLY"

    # Validate constraint manager applies zero penalty for NOT_EVALUABLE
    c_res = cm.validate_candidate(
        vessel_id="CPS_Poseidon",
        vessel_profile={"min_speed_knots": 8.0, "max_speed_knots": 22.0, "deadweight_tonnes": 8500.0, "compatible_fuels": ["bio_methanol"]},
        speed_knots=18.0,
        cargo_allocation=0.0,
        fuel_type="bio_methanol",
        domain_status="VALID",
        envelope_distance=0.0,
        voyage_duration_hours=25.0,
        schedule_deadline_hours=28.0,
        cii_rating=res_voyage["rating"],
        fueleu_compliant=True,
    )
    assert c_res.is_feasible is True
    assert c_res.total_penalty_value == 0.0
    assert "cii_non_compliance" not in c_res.soft_penalties

    # Configured annual non-compliance (annual_context=True, rating 'E')
    res_annual = reg.evaluate_imo_cii(
        vessel_class="passenger_cruise",
        capacity_val=70000.0,
        co2_emissions_tonnes=800.0,
        distance_nm=450.0,
        annual_context=True,
    )
    assert res_annual["rating"] in ["D", "E"]
    c_res_annual = cm.validate_candidate(
        vessel_id="CPS_Poseidon",
        vessel_profile={"min_speed_knots": 8.0, "max_speed_knots": 22.0, "deadweight_tonnes": 8500.0, "compatible_fuels": ["bio_methanol"]},
        speed_knots=18.0,
        cargo_allocation=0.0,
        fuel_type="bio_methanol",
        domain_status="VALID",
        envelope_distance=0.0,
        voyage_duration_hours=25.0,
        schedule_deadline_hours=28.0,
        cii_rating=res_annual["rating"],
        fueleu_compliant=True,
    )
    assert c_res_annual.total_penalty_value > 0.0
    assert "cii_non_compliance" in c_res_annual.soft_penalties


def test_feasibility_probe_scen_01():
    """Verify SCEN-01 (Poseidon) evaluates to feasible with zero penalty for bio_methanol."""
    surrogates = load_real_surrogates()
    scen = BENCHMARK_SCENARIOS["SCEN-01"]
    safe_obj = surrogates[scen.vessel_id]
    evaluator = FleetEvaluationEngine(safe_objective=safe_obj, lambda_robust=0.5)

    dec = VesselAssignmentDecision.from_array(
        np.array([18.0, 0.0, 2.0, 0.0, 1.0]),  # 18 kn, 0 cargo, bio_methanol, transit, shore power
        vessel_id=scen.vessel_id,
        leg_id="scen01_test",
        assigned=True,
    )
    res = evaluator.evaluate_chromosome(
        chromosome=SolutionChromosome(assignments=[dec]),
        voyage_distance_nm=scen.distance_nm,
        schedule_deadline_hours=scen.deadline_hours,
        wave_height_m=scen.wave_height_m,
        wind_speed_ms=scen.wind_speed_ms,
    )

    assert res.is_feasible is True
    assert res.domain_status == "VALID"
    assert res.total_penalty_value == 0.0
    assert len(res.hard_violations) == 0
    assert res.fitness < 10.0  # True physical normalized fitness (~3.18)


def test_safefuelobjective_defense_remains_intact():
    """Verify SafeFuelObjective still blocks adversarial unphysical probes."""
    surrogates = load_real_surrogates()
    safe_obj = surrogates["CPS_Poseidon"]

    # Negative speed
    res_neg = safe_obj.evaluate_candidate({
        "stw_kn": -5.0, "sog_kn": -5.0, "draft_m": 7.5, "displacement_t": 42000.0,
        "wind_speed_ms": 5.0, "wind_direction_deg": 180.0, "wave_height_m": 1.0,
        "wave_period_s": 7.0, "wave_direction_deg": 180.0, "current_speed_ms": 0.5,
        "current_direction_deg": 180.0, "water_depth_m": 100.0,
        "vessel_type": "passenger_cruise", "fuel_type": "vlsfo",
    })
    assert res_neg["domain_status"] == "PHYSICALLY_INVALID"
    assert res_neg["is_valid_candidate"] is False
    assert res_neg["penalized_fuel_objective"] >= 1e5
