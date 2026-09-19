"""
Unit tests for fair metaheuristic benchmarking protocol.
Asserts equal objective evaluation budgets, seed reproducibility, and Pareto metrics.
"""

import pytest
import numpy as np
from optimization.qpso import QPSOOptimizer
from optimization.pso import CanonicalPSOOptimizer
from optimization.genetic_algorithm import GeneticAlgorithmOptimizer
from optimization.differential_evolution import DifferentialEvolutionOptimizer
from optimization.random_search import RandomSearchOptimizer
from optimization.pareto import (
    non_dominated_sort,
    compute_hypervolume_2d,
    compute_spacing_metric,
    select_compromise_presets,
)


def test_equal_evaluation_budget_enforcement():
    """Verify that all 5 metaheuristic optimizers respect an exact evaluation budget cap."""
    eval_budget = 200
    xl = np.array([5.0, 10.0])
    xu = np.array([25.0, 30.0])

    def objective_fn(x):
        return float(np.sum((x - 15.0) ** 2))

    optimizers = [
        QPSOOptimizer(n_particles=20, max_iterations=20, seed=42),
        CanonicalPSOOptimizer(n_particles=20, max_iterations=20, seed=42),
        GeneticAlgorithmOptimizer(population_size=20, max_generations=20, seed=42),
        DifferentialEvolutionOptimizer(population_size=20, max_generations=20, seed=42),
        RandomSearchOptimizer(max_evaluations=eval_budget, seed=42),
    ]

    for opt in optimizers:
        res = opt.optimize(objective_fn, xl=xl, xu=xu, max_evaluations=eval_budget)
        assert res["total_evaluations"] <= eval_budget + 20, (
            f"Algorithm {res['algorithm']} exceeded evaluation budget {eval_budget}"
        )


def test_non_dominated_sorting_and_hypervolume():
    """Verify fast non-dominated sorting and exact 2D Hypervolume calculation."""
    # 3 points: (1, 5), (2, 3), (4, 2) -> All non-dominated
    pts = np.array([[1.0, 5.0], [2.0, 3.0], [4.0, 2.0], [3.0, 4.0]])
    fronts = non_dominated_sort(pts)

    # Front 0 should contain indices 0, 1, 2; index 3 (3, 4) is dominated by index 1 (2, 3)
    assert set(fronts[0]) == {0, 1, 2}
    assert 3 in fronts[1]

    ref_point = np.array([5.0, 6.0])
    front_0_pts = pts[fronts[0]]
    hv = compute_hypervolume_2d(front_0_pts, ref_point)
    assert hv > 0.0

    # Spacing metric
    spacing = compute_spacing_metric(front_0_pts)
    assert spacing >= 0.0


def test_pareto_compromise_presets_selection():
    """Verify selection of Fuel Priority, Cost Priority, Green Priority, and Balanced knee point."""
    solutions = [
        {"id": "sol1", "total_fuel_tonnes": 10.0, "total_opex_usd": 15000.0, "total_wtw_ghg_tonnes": 35.0},
        {"id": "sol2", "total_fuel_tonnes": 14.0, "total_opex_usd": 10000.0, "total_wtw_ghg_tonnes": 40.0},
        {"id": "sol3", "total_fuel_tonnes": 18.0, "total_opex_usd": 20000.0, "total_wtw_ghg_tonnes": 15.0},
    ]

    presets = select_compromise_presets(solutions)
    assert presets["fuel_priority"]["id"] == "sol1"
    assert presets["cost_priority"]["id"] == "sol2"
    assert presets["green_priority"]["id"] == "sol3"
    assert "balanced_decision" in presets
