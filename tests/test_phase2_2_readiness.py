"""
Test Suite: Phase 2.2 Optimization-Readiness & Scientific Validity Gate.
Verifies:
1. Domain checker empirical profile derivation.
2. Out-of-distribution (OOD) detection.
3. Candidate rejection of OOD queries.
4. Physically invalid candidate handling (negative power, impossible speed/power).
5. Prediction interval ordering (q05 <= q50 <= q95).
6. Uncertainty width calculation (q95 - q05).
7. SafeFuelObjective interface structure and outputs.
8. Physics / ML disagreement calculation and diagnostic classification.
9. Deterministic response for fixed inputs.
10. Reproducibility metadata and Git commit hash presence.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from common.reproducibility import get_git_commit
from data.splitting import LeakageSafeSplitter
from prediction.domain_checker import DomainChecker
from prediction.ml_baseline import PureMLPredictor, CONFIG_A_FEATURES
from prediction.physics_predictor import PhysicsFuelPredictor
from prediction.quantile_model import QuantileUncertaintyPredictor
from prediction.safe_objective import SafeFuelObjective


@pytest.fixture(scope="module")
def setup_models():
    pkg_root = Path(__file__).resolve().parent.parent
    data_path = pkg_root / "data" / "synthetic" / "synthetic_vessel_telemetry.csv"
    df_raw = pd.read_csv(data_path)
    clean_mask = (
        df_raw["fuel_mass_flow_kg_h"].notna() &
        (df_raw["fuel_mass_flow_kg_h"] > 0) &
        df_raw["shaft_power_kw"].notna() &
        (df_raw["shaft_power_kw"] >= 0) &
        df_raw["stw_kn"].notna() &
        (df_raw["stw_kn"] > 0) &
        df_raw["sog_kn"].notna() &
        (df_raw["sog_kn"] > 0)
    )
    df_clean = df_raw[clean_mask].drop_duplicates().copy()

    splitter = LeakageSafeSplitter(train_ratio=0.70, val_ratio=0.15, test_ratio=0.15)
    train_df, val_df, test_df = splitter.temporal_split(df_clean)

    ml_model = PureMLPredictor(feature_cols=CONFIG_A_FEATURES, seed=42).fit(train_df=train_df, val_df=val_df)
    quantile_model = QuantileUncertaintyPredictor(feature_cols=CONFIG_A_FEATURES, seed=42).fit(train_df=train_df, val_df=val_df)
    physics_model = PhysicsFuelPredictor()
    domain_checker = DomainChecker(feature_cols=CONFIG_A_FEATURES).fit(train_df)

    safe_objective = SafeFuelObjective(
        ml_predictor=ml_model,
        quantile_predictor=quantile_model,
        physics_predictor=physics_model,
        domain_checker=domain_checker,
        default_lambda_robust=0.5,
    )

    base_candidate = {
        "stw_kn": 14.5,
        "sog_kn": 14.5,
        "draft_m": 8.05,
        "displacement_t": 15250.0,
        "rpm": 120.0,
        "shaft_power_kw": 1800.0,
        "shaft_torque_nm": 140000.0,
        "engine_load_pct": 14.5,
        "wind_speed_ms": 7.0,
        "wind_direction_deg": 180.0,
        "wave_height_m": 1.5,
        "wave_period_s": 7.0,
        "wave_direction_deg": 180.0,
        "current_speed_ms": 0.5,
        "current_direction_deg": 180.0,
        "water_depth_m": 400.0,
        "vessel_type": "container_feeder",
        "fuel_type": "vlsfo",
    }

    return {
        "train_df": train_df,
        "test_df": test_df,
        "domain_checker": domain_checker,
        "safe_objective": safe_objective,
        "base_candidate": base_candidate,
    }


def test_domain_checker_empirical_profile(setup_models):
    """Test 1: Domain checker extracts complete empirical envelope statistics."""
    dc = setup_models["domain_checker"]
    assert dc.is_fitted
    env_df = dc.get_domain_envelope()
    assert len(env_df) == 16  # 16 numerical features
    assert "p01" in env_df.columns
    assert "p99" in env_df.columns
    assert "median" in env_df.columns
    assert (env_df["min"] <= env_df["p01"]).all()
    assert (env_df["p01"] <= env_df["median"]).all()
    assert (env_df["median"] <= env_df["p99"]).all()
    assert (env_df["p99"] <= env_df["max"]).all()


def test_ood_detection(setup_models):
    """Test 2: Domain checker identifies out-of-distribution feature states."""
    dc = setup_models["domain_checker"]
    cand_ood = dict(setup_models["base_candidate"])
    # Set shaft power far beyond training maximum (approx 3574 kW)
    cand_ood["shaft_power_kw"] = 12000.0
    res = dc.evaluate_point(cand_ood)

    assert res["domain_status"] == "OUT_OF_DOMAIN"
    assert res["envelope_distance"] > 0.0
    assert not res["is_valid_candidate"]


def test_candidate_rejection(setup_models):
    """Test 3: SafeFuelObjective explicitly rejects OOD candidates with massive penalty."""
    obj = setup_models["safe_objective"]
    cand_ood = dict(setup_models["base_candidate"])
    cand_ood["shaft_power_kw"] = 14000.0

    eval_res = obj.evaluate_candidate(cand_ood)
    assert eval_res["confidence_risk_flag"] == "REJECTED"
    assert not eval_res["is_valid_candidate"]
    assert eval_res["domain_status"] == "OUT_OF_DOMAIN"
    assert eval_res["penalized_fuel_objective"] > 10000.0


def test_physically_invalid_candidate_handling(setup_models):
    """Test 4: Negative power or impossible speed/power combinations are flagged and rejected."""
    obj = setup_models["safe_objective"]
    
    # Negative shaft power
    cand_neg = dict(setup_models["base_candidate"])
    cand_neg["shaft_power_kw"] = -500.0
    res_neg = obj.evaluate_candidate(cand_neg)
    assert res_neg["domain_status"] == "PHYSICALLY_INVALID"
    assert res_neg["confidence_risk_flag"] == "REJECTED"
    assert res_neg["penalized_fuel_objective"] >= 50000.0

    # High speed with near-zero power (physical impossibility)
    cand_zero = dict(setup_models["base_candidate"])
    cand_zero["stw_kn"] = 20.0
    cand_zero["shaft_power_kw"] = 10.0
    res_zero = obj.evaluate_candidate(cand_zero)
    assert res_zero["domain_status"] == "PHYSICALLY_INVALID"
    assert res_zero["confidence_risk_flag"] == "REJECTED"


def test_prediction_interval_ordering(setup_models):
    """Test 5: Prediction intervals strictly satisfy monotonic non-crossing ordering."""
    obj = setup_models["safe_objective"]
    cand = setup_models["base_candidate"]
    eval_res = obj.evaluate_candidate(cand)

    q05 = eval_res["lower_prediction_bound"]
    q50 = eval_res["median_prediction"]
    q95 = eval_res["upper_prediction_bound"]

    assert q05 <= q50 <= q95, f"Quantiles crossed: q05={q05}, q50={q50}, q95={q95}"


def test_uncertainty_calculation(setup_models):
    """Test 6: Uncertainty width correctly computed as q95 - q05."""
    obj = setup_models["safe_objective"]
    cand = setup_models["base_candidate"]
    eval_res = obj.evaluate_candidate(cand)

    expected_width = eval_res["upper_prediction_bound"] - eval_res["lower_prediction_bound"]
    assert np.isclose(eval_res["uncertainty_width"], expected_width, atol=1e-5)
    assert eval_res["uncertainty_width"] > 0.0


def test_safefuelobjective_interface_structure(setup_models):
    """Test 7: SafeFuelObjective returns all required contract fields."""
    obj = setup_models["safe_objective"]
    cand = setup_models["base_candidate"]
    res = obj.evaluate_candidate(cand)

    required_keys = [
        "predicted_fuel",
        "lower_prediction_bound",
        "median_prediction",
        "upper_prediction_bound",
        "uncertainty_width",
        "robust_fuel_objective",
        "penalized_fuel_objective",
        "physics_reference_fuel",
        "physics_ml_disagreement",
        "disagreement_status",
        "domain_status",
        "envelope_distance",
        "confidence_risk_flag",
        "is_valid_candidate",
        "validity_reason",
    ]
    for k in required_keys:
        assert k in res, f"Missing key in SafeFuelObjective output: {k}"


def test_physics_ml_disagreement_calculation(setup_models):
    """Test 8: Physics/ML model disagreement is correctly computed and classified."""
    obj = setup_models["safe_objective"]
    cand = setup_models["base_candidate"]
    res = obj.evaluate_candidate(cand)

    expected_diff = abs(res["predicted_fuel"] - res["physics_reference_fuel"])
    assert np.isclose(res["physics_ml_disagreement"], expected_diff, atol=1e-4)
    assert res["disagreement_status"] in ["LOW_DISAGREEMENT", "MODERATE_DISAGREEMENT", "HIGH_DISAGREEMENT"]


def test_deterministic_response_for_fixed_inputs(setup_models):
    """Test 9: Fixed inputs yield bitwise identical evaluated objectives."""
    obj = setup_models["safe_objective"]
    cand = setup_models["base_candidate"]

    res1 = obj.evaluate_candidate(cand)
    res2 = obj.evaluate_candidate(cand)

    assert res1["predicted_fuel"] == res2["predicted_fuel"]
    assert res1["lower_prediction_bound"] == res2["lower_prediction_bound"]
    assert res1["upper_prediction_bound"] == res2["upper_prediction_bound"]
    assert res1["robust_fuel_objective"] == res2["robust_fuel_objective"]
    assert res1["penalized_fuel_objective"] == res2["penalized_fuel_objective"]


def test_reproducibility_metadata():
    """Test 10: System verifies valid Git SHA-1 commit hash presence."""
    git_hash = get_git_commit()
    assert git_hash is not None
    assert git_hash != "UNKNOWN_NON_GIT_WORKSPACE"
    assert len(git_hash) == 40
