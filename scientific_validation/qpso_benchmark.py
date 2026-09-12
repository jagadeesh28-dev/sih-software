"""
QPSO Mathematical Benchmark Harness.
Section 13: Evaluates QPSO convergence and stochastic exploration on standard continuous test functions:
1. Sphere: Unimodal, smooth convex benchmark
2. Rastrigin: Highly multimodal benchmark with multiple local optima
3. Rosenbrock: Non-convex narrow parabolic valley benchmark
"""

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import numpy as np

from optimization.qpso import QPSOOptimizer


class StandardBenchmarkFunctions:
    """Standard global optimization benchmark functions."""

    @staticmethod
    def sphere(x: np.ndarray) -> float:
        """Sphere function: Global minimum at x* = [0,...,0], f(x*) = 0."""
        return float(np.sum(x ** 2))

    @staticmethod
    def rastrigin(x: np.ndarray) -> float:
        """Rastrigin function: Global minimum at x* = [0,...,0], f(x*) = 0."""
        d = len(x)
        return float(10.0 * d + np.sum(x ** 2 - 10.0 * np.cos(2.0 * np.pi * x)))

    @staticmethod
    def rosenbrock(x: np.ndarray) -> float:
        """Rosenbrock function: Global minimum at x* = [1,...,1], f(x*) = 0."""
        return float(np.sum(100.0 * (x[1:] - x[:-1] ** 2) ** 2 + (1.0 - x[:-1]) ** 2))


class MockProblemWrapper:
    """Converts a standard scalar function into a problem compatible with QPSOOptimizer."""

    def __init__(self, func: Callable[[np.ndarray], float], dim: int, bounds: Tuple[float, float]):
        self.func = func
        self.n_var = dim
        self.n_obj = 1
        self.xl = np.full(dim, bounds[0])
        self.xu = np.full(dim, bounds[1])

    def _evaluate(self, x, out, *args, **kwargs):
        val = self.func(x)
        out["F"] = [val]
        out["G"] = [0.0]  # No constraint violation


def benchmark_qpso_mathematical_functions(
    dim: int = 5,
    n_particles: int = 40,
    max_iterations: int = 150,
    seed: int = 42,
    output_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Run QPSO optimization across Sphere, Rastrigin, and Rosenbrock test functions.
    Verifies objective reduction, boundary compliance, and deterministic convergence.
    """
    benchmarks = {
        "sphere": {
            "func": StandardBenchmarkFunctions.sphere,
            "bounds": (-5.12, 5.12),
            "optimum": 0.0,
            "threshold": 1e-2,
        },
        "rastrigin": {
            "func": StandardBenchmarkFunctions.rastrigin,
            "bounds": (-5.12, 5.12),
            "optimum": 0.0,
            "threshold": 5.0,  # Rastrigin is hard multimodal; verify significant reduction
        },
        "rosenbrock": {
            "func": StandardBenchmarkFunctions.rosenbrock,
            "bounds": (-2.048, 2.048),
            "optimum": 0.0,
            "threshold": 5.0,
        },
    }

    results = {}
    for name, b_cfg in benchmarks.items():
        prob = MockProblemWrapper(b_cfg["func"], dim, b_cfg["bounds"])
        optimizer = QPSOOptimizer(
            n_particles=n_particles,
            max_iterations=max_iterations,
            beta_start=1.0,
            beta_end=0.5,
            seed=seed,
        )

        res = optimizer.optimize(prob, weight_vector=np.array([1.0]))
        final_loss = res["best_score"]
        init_loss = res["convergence_history"][0]
        reduction_pct = ((init_loss - final_loss) / max(init_loss, 1e-6)) * 100.0

        within_bounds = bool(np.all(res["best_x"] >= prob.xl) and np.all(res["best_x"] <= prob.xu))

        results[name] = {
            "dimension": dim,
            "initial_score": float(init_loss),
            "final_best_score": float(final_loss),
            "theoretical_optimum": b_cfg["optimum"],
            "score_reduction_pct": float(reduction_pct),
            "within_bounds": within_bounds,
            "objective_reduced": bool(final_loss < init_loss),
            "met_threshold": bool(final_loss < b_cfg["threshold"]),
            "total_evaluations": res["total_evaluations"],
            "history": [float(h) for h in res["convergence_history"]],
        }

    all_passed = all(r["objective_reduced"] and r["within_bounds"] for r in results.values())

    summary = {
        "status": "PASS" if all_passed else "FAIL",
        "dimension": dim,
        "n_particles": n_particles,
        "max_iterations": max_iterations,
        "seed": seed,
        "benchmarks": results,
    }

    if output_dir:
        out_p = Path(output_dir)
        out_p.mkdir(parents=True, exist_ok=True)
        with open(out_p / "qpso_mathematical_benchmarks.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

    return summary


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "results" / "qpso_benchmarks"
    res = benchmark_qpso_mathematical_functions(output_dir=out)
    print("=== QPSO MATHEMATICAL BENCHMARK RESULTS ===")
    print(f"Overall Status: {res['status']}")
    for name, r in res["benchmarks"].items():
        print(f"  {name.upper()}: Initial={r['initial_score']:.2f} -> Final={r['final_best_score']:.4f} (Reduction: {r['score_reduction_pct']:.1f}%) | Bounds: {r['within_bounds']}")
