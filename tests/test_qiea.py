"""
Unit Tests for QIEA Feature Selection (SIH26138 - Phase 6).
Verifies Q-bit state normalization, rotation gates, measurement collapse, and entropy.
"""

import numpy as np
import pytest
from src.qi_prediction.qiea import QBitChromosome, QIEAFeatureSelector


def test_qbit_chromosome_normalization():
    """Verify |alpha|^2 + |beta|^2 = 1.0 at initialization and after rotation."""
    chrom = QBitChromosome(n_features=14, seed=42)
    # Check initial superposition
    prob_sum = chrom.alpha**2 + chrom.beta**2
    assert np.allclose(prob_sum, 1.0, atol=1e-10)
    assert np.allclose(chrom.alpha, 1.0 / np.sqrt(2.0), atol=1e-10)
    assert np.allclose(chrom.beta, 1.0 / np.sqrt(2.0), atol=1e-10)

    # Perform measurement
    mask = chrom.measure()
    assert len(mask) == 14
    assert np.all(np.isin(mask, [0, 1]))
    assert np.sum(mask) >= 1  # Safety guard: at least 1 feature selected

    # Apply rotation gate
    best_b = np.ones(14, dtype=int)
    chrom.apply_rotation_gate(current_x=mask, best_b=best_b, is_better=False, theta_step=0.05 * np.pi)
    prob_sum_after = chrom.alpha**2 + chrom.beta**2
    assert np.allclose(prob_sum_after, 1.0, atol=1e-10)


def test_qiea_shannon_entropy_decay():
    """Verify initial Shannon entropy is 1.0 and decays as the algorithm converges."""
    chrom = QBitChromosome(n_features=10, seed=42)
    initial_entropy = chrom.get_shannon_entropy()
    assert np.isclose(initial_entropy, 1.0, atol=1e-5)

    # Force rotations toward state |1>
    curr_x = np.zeros(10, dtype=int)
    best_b = np.ones(10, dtype=int)
    for _ in range(15):
        chrom.apply_rotation_gate(current_x=curr_x, best_b=best_b, is_better=False, theta_step=0.05 * np.pi)

    final_entropy = chrom.get_shannon_entropy()
    assert final_entropy < initial_entropy
    assert final_entropy >= 0.0


def test_qiea_feature_search_optimization():
    """Verify QIEA finds known optimal feature subset on synthetic sphere problem."""
    # Synthetic objective: optimal features are {2, 5, 8}
    target_subset = {2, 5, 8}

    def dummy_eval(mask: np.ndarray) -> float:
        selected = set(np.where(mask == 1)[0])
        # Penalty for missing target features + penalty for extraneous features
        missing = len(target_subset - selected)
        extra = len(selected - target_subset)
        return float(missing * 10.0 + extra * 2.0)

    qiea = QIEAFeatureSelector(population_size=10, max_generations=20, seed=42)
    res = qiea.search(n_features=10, eval_fn=dummy_eval)

    assert res["best_score"] < 10.0
    assert res["total_evaluations"] == 200
    assert len(res["convergence_history"]) == 20
    assert res["convergence_history"][-1] <= res["convergence_history"][0]
