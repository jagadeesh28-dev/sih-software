"""
Phase 4 Regression Check:
Verifies that A0 (Plain QPSO) reproduces the exact Phase 4 failure behavior on seeds 1005, 1021, 1025, 1029.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(".").resolve()))

from optimization.fleet_evaluator_phase4 import Phase4FleetEvaluator
from experiments.exp_phase3_master_runner import load_real_surrogates
from src.evaluator.common_evaluator import CommonFleetEvaluator
from src.algorithms.qpso import PlainQPSOOptimizer

def test_regression():
    print("Loading real surrogates...")
    surrogates = load_real_surrogates()
    evaluator = Phase4FleetEvaluator(surrogates=surrogates, lambda_robust=0.50)
    xl, xu = evaluator.get_bounds()

    failed_seeds = [1005, 1021, 1025, 1029]
    passing_seeds = [1001, 1002]

    print("Checking known passing seeds:")
    for s in passing_seeds:
        comm = CommonFleetEvaluator(evaluator, max_budget=2500)
        opt = PlainQPSOOptimizer(seed=s, n_particles=50, max_iterations=50)
        res = opt.optimize(comm, xl, xu, budget=2500)
        print(f"Seed {s}: feasible={res.feasible_at_end}, fitness={res.best_fitness:.2f}, pen={res.best_penalty:.2f}")

    print("\nChecking known failing seeds:")
    for s in failed_seeds:
        comm = CommonFleetEvaluator(evaluator, max_budget=2500)
        opt = PlainQPSOOptimizer(seed=s, n_particles=50, max_iterations=50)
        res = opt.optimize(comm, xl, xu, budget=2500)
        print(f"Seed {s}: feasible={res.feasible_at_end}, fitness={res.best_fitness:.2f}, pen={res.best_penalty:.2f}, violations={res.hard_violations}")

if __name__ == "__main__":
    test_regression()
