"""
Test Suite: Phase 2.3 Real Maritime Data Validation & Model Transfer.
Verifies:
1. Real data pipeline ingestion, canonical transformation, and zero target nulls.
2. Vector STW derivation, closure benchmark on Poseidon, and frozen sensor detection on Triton.
3. Operating regime classification completeness.
4. Chronological split integrity (zero temporal or future leakage).
5. CONFIG-REAL-A and CONFIG-REAL-B feature sets and inference.
6. DomainChecker envelope derivation on real telemetry and SafeFuelObjective barrier penalties.
7. Synthetic-to-real transfer failure documentation.
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from data.real_data_pipeline import RealMaritimeDataPipeline, compute_vector_stw, classify_operating_regimes
from prediction.domain_checker import DomainChecker
from prediction.ml_baseline import PureMLPredictor
from prediction.physics_predictor import PhysicsFuelPredictor
from prediction.quantile_model import QuantileUncertaintyPredictor
from prediction.safe_objective import SafeFuelObjective

REPO_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = REPO_ROOT / "data" / "processed" / "real" / "fuelcast"
RESULTS_DIR = REPO_ROOT / "results" / "experiments" / "real_validation"


@pytest.fixture(scope="module")
def load_processed_vessels():
    vessels = ["CPS_Poseidon", "CPS_Triton", "OSS_Ceto"]
    dfs = {}
    for v in vessels:
        p = PROCESSED_DIR / f"{v}.parquet"
        assert p.exists(), f"Processed parquet missing: {p}"
        dfs[v] = pd.read_parquet(p)
    return dfs


def test_real_data_pipeline_ingestion(load_processed_vessels):
    """Test 1: Verify processed row counts, canonical fields, and zero target nulls."""
    dfs = load_processed_vessels
    assert len(dfs["CPS_Poseidon"]) == 105422
    assert len(dfs["CPS_Triton"]) == 25347
    assert len(dfs["OSS_Ceto"]) == 43205

    for v_name, df in dfs.items():
        assert "fuel_mass_flow_kg_h" in df.columns
        assert "stw_kn" in df.columns
        assert "sog_kn" in df.columns
        assert "shaft_power_kw" in df.columns
        assert "operating_regime" in df.columns

        # Target verification
        assert df["fuel_mass_flow_kg_h"].isna().sum() == 0
        assert (df["fuel_mass_flow_kg_h"] >= 0.0).all()
        assert df["stw_kn"].isna().sum() == 0
        assert (df["stw_kn"] >= 0.0).all()


def test_vector_stw_closure_and_frozen_detection(load_processed_vessels):
    """Test 2: Verify frozen Doppler log on Triton and vector closure agreement on Poseidon."""
    dfs = load_processed_vessels

    # 1. Triton frozen sensor detection
    df_tri = dfs["CPS_Triton"]
    assert "stw_raw_kn" in df_tri.columns
    assert np.isclose(df_tri["stw_raw_kn"], 1.0, atol=1e-3).all()
    assert df_tri["stw_status"].iloc[0] == "DERIVED_VECTOR"
    assert df_tri["stw_kn"].std() > 1.0  # Vector STW restored dynamic variation

    # 2. Poseidon vector closure
    df_pos = dfs["CPS_Poseidon"]
    actual_stw = df_pos["stw_ms"].values
    vec_stw = df_pos["vector_stw_ms"].values
    corr = float(np.corrcoef(actual_stw, vec_stw)[0, 1])
    assert corr > 0.99, f"Vector closure correlation on Poseidon {corr} must exceed 0.99"


def test_operating_regime_classification(load_processed_vessels):
    """Test 3: Verify regime classification covers stopped, maneuvering, cruising, and rough sea."""
    dfs = load_processed_vessels
    for v_name, df in dfs.items():
        regimes = set(df["operating_regime"].unique())
        assert "STOPPED_HARBOR" in regimes
        assert "MANEUVERING" in regimes
        assert "NORMAL_CRUISING" in regimes
        assert df["operating_regime"].isna().sum() == 0


def test_chronological_split_manifest():
    """Test 4: Verify chronological split manifest has zero temporal leakage."""
    manifest_file = REPO_ROOT / "07_REAL_SPLIT_MANIFEST.json"
    assert manifest_file.exists()

    with open(manifest_file, "r") as f:
        manifest = json.load(f)

    for v_name, splits in manifest["chronological_splits"].items():
        tr = splits["train"]
        va = splits["validation"]
        te = splits["test"]

        assert tr["end_idx"] == va["start_idx"]
        assert va["end_idx"] == te["start_idx"]
        assert tr["start_idx"] == 0
        assert te["end_idx"] == splits["total_rows"]


def test_config_real_a_and_b_inference(load_processed_vessels):
    """Test 5: Verify models train and infer with CONFIG-REAL-A (no power) and CONFIG-REAL-B."""
    df_sample = load_processed_vessels["CPS_Triton"].head(500)
    train_df = df_sample.iloc[:350]
    test_df = df_sample.iloc[350:]

    config_a = [
        "stw_kn", "sog_kn", "draft_m", "displacement_t",
        "wind_speed_ms", "wind_direction_deg", "wave_height_m", "wave_period_s",
        "wave_direction_deg", "current_speed_ms", "current_direction_deg",
        "water_depth_m", "vessel_type", "fuel_type"
    ]
    # CONFIG-A must NOT have shaft power or RPM
    assert "shaft_power_kw" not in config_a
    assert "rpm" not in config_a

    ml_a = PureMLPredictor(feature_cols=config_a, seed=42).fit(train_df)
    preds_a = ml_a.predict(test_df)
    assert len(preds_a) == len(test_df)
    assert (preds_a > 0).all()

    config_b = config_a + ["shaft_power_kw", "rpm", "shaft_torque_nm", "engine_load_pct"]
    ml_b = PureMLPredictor(feature_cols=config_b, seed=42).fit(train_df)
    preds_b = ml_b.predict(test_df)
    assert len(preds_b) == len(test_df)
    assert (preds_b > 0).all()


def test_domain_checker_and_safe_objective_real(load_processed_vessels):
    """Test 6: Verify DomainChecker fits on real data and SafeFuelObjective enforces penalties."""
    df_sample = load_processed_vessels["CPS_Triton"].head(600)
    train_df = df_sample.iloc[:400]

    features = [
        "stw_kn", "sog_kn", "draft_m", "displacement_t",
        "wind_speed_ms", "wind_direction_deg", "wave_height_m", "wave_period_s",
        "wave_direction_deg", "current_speed_ms", "current_direction_deg",
        "water_depth_m", "shaft_power_kw", "rpm", "shaft_torque_nm",
        "engine_load_pct", "vessel_type", "fuel_type"
    ]

    dc = DomainChecker(feature_cols=features).fit(train_df)
    assert dc.is_fitted

    ml = PureMLPredictor(feature_cols=features, seed=42).fit(train_df)
    qm = QuantileUncertaintyPredictor(feature_cols=features, seed=42).fit(train_df)
    phys = PhysicsFuelPredictor()

    safe_obj = SafeFuelObjective(ml_predictor=ml, quantile_predictor=qm, physics_predictor=phys, domain_checker=dc)

    # Test adversarial negative power state
    cand_neg = train_df.iloc[0].to_dict()
    cand_neg["shaft_power_kw"] = -100.0

    eval_res = safe_obj.evaluate_candidate(cand_neg)
    assert eval_res["confidence_risk_flag"] == "REJECTED"
    assert eval_res["domain_status"] == "PHYSICALLY_INVALID"
    assert eval_res["penalized_fuel_objective"] >= 10000.0


def test_synthetic_transfer_failure_documented():
    """Test 7: Verify 09_SYNTHETIC_TO_REAL_TRANSFER.csv exists and documents transfer failure."""
    fpath = REPO_ROOT / "09_SYNTHETIC_TO_REAL_TRANSFER.csv"
    assert fpath.exists()
    df = pd.read_csv(fpath)
    # Fleet test R2 must be negative reflecting transfer failure
    fleet_r2 = df.loc[df["Test_Target"] == "Combined Fleet Test", "R2"].iloc[0]
    assert fleet_r2 < 0.0, f"Synthetic transfer R2 {fleet_r2} must be negative reflecting domain shift failure"
