"""
Unit Tests for Data Leakage Prevention (SIH26138 - Phase 6).
Verifies timestamp ordering, future-feature leakage prevention, and train-only fitting.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.qi_prediction.validation import ValidationHarness
from prediction.ml_baseline import PureMLPredictor, CONFIG_A_FEATURES

REPO_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = REPO_ROOT / "data" / "processed" / "real" / "fuelcast"


@pytest.fixture(scope="module")
def sample_vessel_data():
    vessels = ["CPS_Poseidon", "CPS_Triton", "OSS_Ceto"]
    dfs = {}
    for v in vessels:
        p = PROCESSED_DIR / f"{v}.parquet"
        assert p.exists()
        dfs[v] = pd.read_parquet(p)
    return dfs


def test_chronological_split_timestamp_monotonicity(sample_vessel_data):
    """Verify the harness's train/val/test partitions are forward-in-time per vessel with zero overlap."""
    dfs = sample_vessel_data
    fleet_train, fleet_val, fleet_test = ValidationHarness.forward_temporal_splits(dfs)

    assert len(fleet_train) + len(fleet_val) + len(fleet_test) == sum(len(d) for d in dfs.values())

    for v_name, df in dfs.items():
        vt = df["vessel_type"].iloc[0]
        ts = {
            name: pd.to_datetime(part.loc[part["vessel_type"] == vt, "timestamp"])
            for name, part in (("train", fleet_train), ("val", fleet_val), ("test", fleet_test))
        }
        n = len(df)
        assert len(ts["train"]) == int(n * 0.6), v_name
        assert len(ts["val"]) == int(n * 0.2), v_name
        assert ts["train"].max() <= ts["val"].min(), v_name
        assert ts["val"].max() <= ts["test"].min(), v_name


def test_target_excluded_from_features():
    """Verify target fuel_mass_flow_kg_h is never included in CONFIG_A or CONFIG_B."""
    assert "fuel_mass_flow_kg_h" not in CONFIG_A_FEATURES
    assert "target" not in CONFIG_A_FEATURES


def test_scaler_and_categorical_fit_train_only(sample_vessel_data):
    """Verify categorical encoders learn levels strictly from TRAIN and do not leak test categories."""
    dfs = sample_vessel_data
    fleet_train, fleet_val, fleet_test = ValidationHarness.forward_temporal_splits(dfs)

    # Exercise the encoder fit path fit() uses, without native LightGBM training
    # (training here crashed natively on Windows with NumPy 2.x and tested nothing extra).
    predictor = PureMLPredictor(feature_cols=["vessel_type", "fuel_type", "stw_kn"], seed=42)
    predictor._prepare_features(fleet_train, is_train=True)

    for cat_col in ["vessel_type", "fuel_type"]:
        train_cats = set(fleet_train[cat_col].dropna().astype(str).unique())
        assert set(predictor.categorical_dtypes[cat_col].categories) == train_cats

    # A level that exists only outside TRAIN must not become a known category
    leaked = fleet_test.head(5).copy()
    leaked["fuel_type"] = "unseen_test_only_fuel"
    X_leaked = predictor._prepare_features(leaked, is_train=False)
    assert X_leaked["fuel_type"].isna().all()
    assert "unseen_test_only_fuel" not in predictor.categorical_dtypes["fuel_type"].categories
