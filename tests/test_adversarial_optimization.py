"""
Unit tests for adversarial optimization and defensive surrogate interception.
Proves that SafeFuelObjective repels ungrounded troughs during active optimization loops.
"""

import pytest
import numpy as np
import pandas as pd

from prediction.domain_checker import DomainChecker
from prediction.ml_baseline import PureMLPredictor
from prediction.physics_predictor import PhysicsFuelPredictor
from prediction.quantile_model import QuantileUncertaintyPredictor
from prediction.safe_objective import SafeFuelObjective
from optimization.qpso import QPSOOptimizer


@pytest.fixture(scope="module")
def safe_objective_fixture():
    """Construct lightweight fitted SafeFuelObjective for adversarial testing."""
    # Synthetic calibration partition
    np.random.seed(42)
    n = 200
    df_train = pd.DataFrame({
        "stw_kn": np.random.uniform(10.0, 20.0, n),
        "sog_kn": np.random.uniform(10.0, 20.0, n),
        "draft_m": np.random.uniform(6.0, 8.0, n),
        "displacement_t": np.random.uniform(15000.0, 25000.0, n),
        "wind_speed_ms": np.random.uniform(2.0, 12.0, n),
        "wind_direction_deg": np.random.uniform(0.0, 360.0, n),
        "wave_height_m": np.random.uniform(0.5, 3.0, n),
        "wave_period_s": np.random.uniform(4.0, 10.0, n),
        "wave_direction_deg": np.random.uniform(0.0, 360.0, n),
        "current_speed_ms": np.random.uniform(0.1, 1.0, n),
        "current_direction_deg": np.random.uniform(0.0, 360.0, n),
        "water_depth_m": np.random.uniform(50.0, 500.0, n),
        "vessel_type": ["cruise_passenger"] * n,
        "fuel_type": ["vlsfo"] * n,
    })
    # Realistic quadratic fuel curve
    df_train["fuel_mass_flow_kg_h"] = 1500.0 + 3.5 * (df_train["stw_kn"] ** 2.2) + 20.0 * df_train["wave_height_m"]

    domain_checker = DomainChecker(feature_cols=list(df_train.columns[:-1])).fit(df_train)
    ml_pred = PureMLPredictor(feature_cols=list(df_train.columns[:-1]), seed=42).fit(df_train)
    q_pred = QuantileUncertaintyPredictor(feature_cols=list(df_train.columns[:-1]), seed=42).fit(df_train)
    phys_pred = PhysicsFuelPredictor(default_vessel_type="container_feeder")

    return SafeFuelObjective(
        ml_predictor=ml_pred,
        quantile_predictor=q_pred,
        physics_predictor=phys_pred,
        domain_checker=domain_checker,
        penalty_constant=10000.0,
    )


def test_adversarial_speed_exploitation_interception(safe_objective_fixture):
    """
    Test that an optimizer searching over ungrounded speed ranges [5.0, 35.0 kn]
    is repelled from the ungrounded high-speed zone (>20 kn) by SafeFuelObjective.
    """
    safe_obj = safe_objective_fixture

    def eval_fn(x):
        speed = float(x[0])
        cand = {
            "stw_kn": speed,
            "sog_kn": speed,
            "draft_m": 7.0,
            "displacement_t": 20000.0,
            "wind_speed_ms": 7.0,
            "wind_direction_deg": 180.0,
            "wave_height_m": 1.5,
            "wave_period_s": 7.0,
            "wave_direction_deg": 180.0,
            "current_speed_ms": 0.5,
            "current_direction_deg": 180.0,
            "water_depth_m": 250.0,
            "vessel_type": "cruise_passenger",
            "fuel_type": "vlsfo",
        }
        res = safe_obj.evaluate_candidate(cand)
        return float(res["penalized_fuel_objective"])

    # Search space includes ungrounded high speeds up to 35 kn
    xl = np.array([5.0])
    xu = np.array([35.0])

    qpso = QPSOOptimizer(n_particles=25, max_iterations=40, seed=42)
    res = qpso.optimize(eval_fn, xl=xl, xu=xu)

    best_speed = float(res["best_x"][0])
    # The optimal speed found must be within the valid training envelope [10.0, 20.0 kn]
    # because > 20 kn triggers barrier penalties
    assert best_speed <= 20.5, f"Optimizer exploited ungrounded speed: {best_speed} kn"
    assert res["best_score"] < 10000.0, "Optimizer reported an out-of-domain penalty as optimal"
