"""
Unit Tests for QPSO Hyperparameter Optimization (SIH26138 - Phase 6).
Verifies delta-potential well dynamics, mean best position, and bounds handling.
"""

import numpy as np
import pytest
from src.qi_prediction.qpso import (
    HyperparameterSearchSpace,
    QPSOOptimizer,
    ClassicalPSOOptimizer,
    RandomSearchOptimizer,
)


def test_hyperparameter_search_space_mapping():
    """Verify vector in [0, 1]^d maps to valid parameter bounds."""
    dim = HyperparameterSearchSpace.get_dim()
    assert dim == 8

    # Test lower bound vector
    v_low = np.zeros(dim)
    p_low = HyperparameterSearchSpace.vector_to_params(v_low)
    assert p_low["learning_rate"] == 0.01
    assert p_low["num_leaves"] == 15
    assert p_low["max_depth"] == 3
    assert p_low["alpha_residual"] == 0.5

    # Test upper bound vector
    v_high = np.ones(dim)
    p_high = HyperparameterSearchSpace.vector_to_params(v_high)
    assert p_high["learning_rate"] == 0.20
    assert p_high["num_leaves"] == 63
    assert p_high["max_depth"] == 8
    assert p_high["alpha_residual"] == 1.0


def test_qpso_delta_potential_optimization():
    """Verify QPSO minimizes a multi-dimensional continuous benchmark function."""
    # Target optimum at [0.5, 0.5, ...]
    dim = HyperparameterSearchSpace.get_dim()
    target = np.full(dim, 0.5)

    def sphere_obj(params: dict) -> float:
        # Reconstruct vector
        v = []
        for name, low, high, p_type in HyperparameterSearchSpace.BOUNDS:
            val = params[name]
            if p_type in ["float", "int"]:
                norm_val = (val - low) / (high - low)
            elif p_type == "log_float":
                norm_val = (np.log10(val) - np.log10(low)) / (np.log10(high) - np.log10(low))
            v.append(norm_val)
        vec = np.array(v)
        return float(np.sum((vec - target) ** 2))

    qpso = QPSOOptimizer(n_particles=15, max_iterations=12, seed=42)
    res = qpso.optimize(sphere_obj)

    assert res["evaluations"] == 15 * 12
    assert res["best_score"] < 0.5
    assert len(res["convergence_history"]) == 12
    assert res["convergence_history"][-1] <= res["convergence_history"][0]


def test_classical_pso_control():
    """Verify Classical PSO control functions with identical budget."""
    dim = HyperparameterSearchSpace.get_dim()

    def dummy_obj(params: dict) -> float:
        return float(params["learning_rate"] * 10.0)

    cpso = ClassicalPSOOptimizer(n_particles=15, max_iterations=10, seed=42)
    res = cpso.optimize(dummy_obj)

    assert res["evaluations"] == 150
    assert "best_score" in res
    assert "best_params" in res
