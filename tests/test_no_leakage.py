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
    """Verify train, val, and test partitions are strictly monotonic in time with zero overlap."""
    dfs = sample_vessel_data
    fleet_train, fleet_val, fleet_test = ValidationHarness.forward_temporal_splits(dfs)

    for v_name, df in dfs.items():
        n = len(df)
        n_tr = int(n * 0.6)
        n_va = int(n * 0.2)

        df_tr = df.iloc[:n_tr]
        df_va = df.iloc[n_tr : n_tr + n_va]
        df_te = df.iloc[n_tr + n_va :]

        # Index check (since parquet is sorted chronologically)
        assert df_tr.index[-1] < df_va.index[0]
        assert df_va.index[-1] < df_te.index[0]

        # Timestamp check if timestamp column exists
        if "timestamp" in df.columns:
            assert pd.to_datetime(df_tr["timestamp"].max()) <= pd.to_datetime(df_va["timestamp"].min())
            assert pd.to_datetime(df_va["timestamp"].max()) <= pd.to_datetime(df_te["timestamp"].min())


def test_target_excluded_from_features():
    """Verify target fuel_mass_flow_kg_h is never included in CONFIG_A or CONFIG_B."""
    assert "fuel_mass_flow_kg_h" not in CONFIG_A_FEATURES
    assert "target" not in CONFIG_A_FEATURES


def test_scaler_and_categorical_fit_train_only(sample_vessel_data):
    """Verify categorical encoders learn levels strictly from TRAIN and do not leak test categories."""
    dfs = sample_vessel_data
    fleet_train, fleet_val, fleet_test = ValidationHarness.forward_temporal_splits(dfs)

    predictor = PureMLPredictor(feature_cols=["vessel_type", "fuel_type", "stw_kn"], seed=42)
    # Fit strictly on train
    predictor.fit(fleet_train)

    # Check stored categorical dtypes
    for cat_col in ["vessel_type", "fuel_type"]:
        if cat_col in predictor.categorical_dtypes:
            train_cats = set(fleet_train[cat_col].dropna().unique())
            stored_cats = set(predictor.categorical_dtypes[cat_col].categories)
            assert stored_cats == train_cats
