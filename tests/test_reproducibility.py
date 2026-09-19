"""
Unit Tests for Seed Reproducibility (SIH26138 - Phase 6).
Verifies exact bitwise and trajectory reproducibility for QIEA, QPSO, and ML models.
"""

import numpy as np
import pytest
import lightgbm as lgb
from src.qi_prediction.qiea import QIEAFeatureSelector
from src.qi_prediction.qpso import QPSOOptimizer, HyperparameterSearchSpace


def test_qiea_seed_determinism():
    """Verify QIEA produces bitwise identical feature masks and trajectories under same seed."""
    def dummy_eval(mask: np.ndarray) -> float:
        return float(np.sum((mask - np.array([1, 0, 1, 0, 1, 1, 0, 0, 1, 0])) ** 2))

    qiea1 = QIEAFeatureSelector(population_size=8, max_generations=10, seed=42)
    res1 = qiea1.search(n_features=10, eval_fn=dummy_eval)

    qiea2 = QIEAFeatureSelector(population_size=8, max_generations=10, seed=42)
    res2 = qiea2.search(n_features=10, eval_fn=dummy_eval)

    assert np.array_equal(res1["best_mask"], res2["best_mask"])
    assert np.isclose(res1["best_score"], res2["best_score"], atol=1e-12)
    assert np.allclose(res1["convergence_history"], res2["convergence_history"], atol=1e-12)


def test_qpso_seed_determinism():
    """Verify QPSO produces identical vectors and convergence history under same seed."""
    dim = HyperparameterSearchSpace.get_dim()

    def dummy_obj(params: dict) -> float:
        return float(params["learning_rate"] * 2.0 + params["num_leaves"])

    qpso1 = QPSOOptimizer(n_particles=10, max_iterations=8, seed=42)
    res1 = qpso1.optimize(dummy_obj)

    qpso2 = QPSOOptimizer(n_particles=10, max_iterations=8, seed=42)
    res2 = qpso2.optimize(dummy_obj)

    assert np.allclose(res1["best_vector"], res2["best_vector"], atol=1e-10)
    assert np.isclose(res1["best_score"], res2["best_score"], atol=1e-10)
    assert np.allclose(res1["convergence_history"], res2["convergence_history"], atol=1e-10)


def test_lightgbm_seed_determinism():
    """Verify LightGBM model fits bitwise identically under fixed seed."""
    rng = np.random.default_rng(42)
    X = rng.normal(0, 1, size=(200, 5))
    y = X[:, 0] * 2.0 + X[:, 1]

    m1 = lgb.LGBMRegressor(n_estimators=30, random_state=42, n_jobs=1, verbose=-1)
    m1.fit(X, y)
    p1 = m1.predict(X)

    m2 = lgb.LGBMRegressor(n_estimators=30, random_state=42, n_jobs=1, verbose=-1)
    m2.fit(X, y)
    p2 = m2.predict(X)

    assert np.allclose(p1, p2, atol=1e-12)
