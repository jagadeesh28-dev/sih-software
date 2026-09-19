"""
Unit Tests for Direct QI Matrix Product State (MPS) Regressor (SIH26138 - Phase 6).
Verifies quantum feature mapping, MPS tensor contraction, and classical polynomial control.
"""

import numpy as np
import pandas as pd
import pytest
from src.qi_prediction.mps_predictor import QIMPSPredictor, ClassicalPolyPredictor


def test_quantum_feature_map_unit_norm():
    """Verify trigonometric feature map satisfies ||phi(x)||^2 = 1.0."""
    cols = ["f1", "f2", "f3"]
    mps = QIMPSPredictor(feature_cols=cols, bond_dim=2, seed=42)

    X_test = np.array([
        [0.0, 0.5, 1.0],
        [0.25, 0.75, 0.1],
    ])
    phi = mps._feature_map(X_test)
    assert phi.shape == (2, 3, 2)

    # For each sample and feature, norm must be 1.0
    norms = np.sum(phi**2, axis=-1)
    assert np.allclose(norms, 1.0, atol=1e-10)


def test_mps_fit_predict_pipeline():
    """Verify MPS predictor fits and generates 1D continuous predictions."""
    rng = np.random.default_rng(42)
    N = 200
    df = pd.DataFrame({
        "stw_kn": rng.uniform(8.0, 20.0, N),
        "sog_kn": rng.uniform(8.0, 20.0, N),
        "draft_m": rng.uniform(6.0, 12.0, N),
    })
    # Target residual with non-linear interaction
    r = 2.0 * df["stw_kn"].values + 0.5 * (df["draft_m"].values ** 2) + rng.normal(0, 1, N)

    mps = QIMPSPredictor(feature_cols=["stw_kn", "sog_kn", "draft_m"], bond_dim=3, epochs=5, seed=42)
    mps.fit(df, r)
    preds = mps.predict(df)

    assert preds.shape == (N,)
    assert not np.isnan(preds).any()
    assert not np.isinf(preds).any()


def test_classical_poly_control():
    """Verify Classical Polynomial predictor baseline fits and predicts."""
    rng = np.random.default_rng(42)
    N = 100
    df = pd.DataFrame({
        "stw_kn": rng.uniform(8.0, 20.0, N),
        "draft_m": rng.uniform(6.0, 12.0, N),
    })
    r = df["stw_kn"].values * df["draft_m"].values

    poly = ClassicalPolyPredictor(feature_cols=["stw_kn", "draft_m"], ridge_alpha=1.0, seed=42)
    poly.fit(df, r)
    preds = poly.predict(df)

    assert preds.shape == (N,)
    assert not np.isnan(preds).any()
