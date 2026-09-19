"""
Unit tests for FleetEvaluationEngine, SolutionChromosome, and scenario execution.
"""

import pytest
import numpy as np
import pandas as pd

from prediction.domain_checker import DomainChecker
from prediction.ml_baseline import PureMLPredictor
from prediction.physics_predictor import PhysicsFuelPredictor
from prediction.quantile_model import QuantileUncertaintyPredictor
from prediction.safe_objective import SafeFuelObjective
from optimization.evaluator import FleetEvaluationEngine
from optimization.variables import SolutionChromosome, VesselAssignmentDecision
from optimization.scenarios import BENCHMARK_SCENARIOS, create_baseline_policy


@pytest.fixture(scope="module")
def fleet_evaluator_fixture():
    """Build fitted FleetEvaluationEngine."""
    np.random.seed(42)
    n = 200
    df_train = pd.DataFrame({
        "stw_kn": np.random.uniform(8.0, 22.0, n),
        "sog_kn": np.random.uniform(8.0, 22.0, n),
        "draft_m": np.random.uniform(6.0, 8.5, n),
        "displacement_t": np.random.uniform(15000.0, 95000.0, n),
        "wind_speed_ms": np.random.uniform(2.0, 15.0, n),
        "wind_direction_deg": np.random.uniform(0.0, 360.0, n),
        "wave_height_m": np.random.uniform(0.5, 4.0, n),
        "wave_period_s": np.random.uniform(4.0, 11.0, n),
        "wave_direction_deg": np.random.uniform(0.0, 360.0, n),
        "current_speed_ms": np.random.uniform(0.1, 1.2, n),
        "current_direction_deg": np.random.uniform(0.0, 360.0, n),
        "water_depth_m": np.random.uniform(50.0, 1000.0, n),
        "vessel_type": ["cruise_passenger"] * n,
        "fuel_type": ["vlsfo"] * n,
    })
    df_train["fuel_mass_flow_kg_h"] = 1800.0 + 3.0 * (df_train["stw_kn"] ** 2.3)

    domain_checker = DomainChecker(feature_cols=list(df_train.columns[:-1])).fit(df_train)
    ml_pred = PureMLPredictor(feature_cols=list(df_train.columns[:-1]), seed=42).fit(df_train)
    q_pred = QuantileUncertaintyPredictor(feature_cols=list(df_train.columns[:-1]), seed=42).fit(df_train)
    phys_pred = PhysicsFuelPredictor(default_vessel_type="container_feeder")

    safe_obj = SafeFuelObjective(
        ml_predictor=ml_pred,
        quantile_predictor=q_pred,
        physics_predictor=phys_pred,
        domain_checker=domain_checker,
        penalty_constant=10000.0,
    )

    return FleetEvaluationEngine(safe_objective=safe_obj)


def test_evaluate_single_voyage_chromosome(fleet_evaluator_fixture):
    """Verify complete evaluation pipeline for a candidate chromosome."""
    evaluator = fleet_evaluator_fixture
    scenario = BENCHMARK_SCENARIOS["SCEN-01"]

    chrom = SolutionChromosome(
        assignments=[
            VesselAssignmentDecision(
                vessel_id="CPS_Poseidon",
                leg_id="leg1",
                assigned=True,
                speed_knots=18.0,
                fuel_type="vlsfo",
                cargo_allocation_teu=0.0,
                operating_mode="transit",
                use_shore_power_at_dest=True,
            )
        ]
    )

    res = evaluator.evaluate_chromosome(
        chromosome=chrom,
        voyage_distance_nm=scenario.distance_nm,
        schedule_deadline_hours=scenario.deadline_hours,
        wave_height_m=scenario.wave_height_m,
        wind_speed_ms=scenario.wind_speed_ms,
    )

    assert res.total_fuel_tonnes > 0.0
    assert res.total_opex_usd > 0.0
    assert res.total_wtw_ghg_tonnes > 0.0
    assert res.voyage_duration_hours > 0.0
    assert len(res.objective_vector) == 5
    assert res.is_feasible is True
    assert "Strategy evaluated" in res.explanation


def test_baseline_policy_generation(fleet_evaluator_fixture):
    """Verify generation and evaluation of standard BASELINE-1 through BASELINE-6."""
    evaluator = fleet_evaluator_fixture
    scenario = BENCHMARK_SCENARIOS["SCEN-01"]

    b1 = create_baseline_policy("BASELINE-1", scenario)  # Max speed
    b3 = create_baseline_policy("BASELINE-3", scenario)  # Fuel-minimizing speed

    res_b1 = evaluator.evaluate_chromosome(b1, scenario.distance_nm, scenario.deadline_hours)
    res_b3 = evaluator.evaluate_chromosome(b3, scenario.distance_nm, scenario.deadline_hours)

    # Fuel-minimizing speed should yield lower or equal fuel than max speed
    assert res_b3.total_fuel_tonnes <= res_b1.total_fuel_tonnes
    assert res_b1.voyage_duration_hours < res_b3.voyage_duration_hours
