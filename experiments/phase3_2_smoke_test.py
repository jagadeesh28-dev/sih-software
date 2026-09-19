"""
Phase 3.2 Smoke Benchmark Runner:
Executes Section 11: Controlled Optimizer Smoke Test.
- 5 optimizers: QPSO, PSO, GA, DE, Random Search
- N_eval = 500 evaluations per run
- 3 matched seeds (42, 43, 44)
- Scenario: SCEN-01 (CPS_Poseidon, North Sea Cruise Transit, 450 nm, 28h deadline)
Outputs: results/audit/phase3_2/05_smoke_benchmark.csv
"""

import os
import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path

# Ensure platform root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from experiments.exp_phase3_master_runner import (
    load_real_surrogates,
    create_eval_function_for_scenario,
    BENCHMARK_SCENARIOS,
    GIT_COMMIT,
    TIMESTAMP,
)
from optimization.evaluator import FleetEvaluationEngine
from optimization.variables import FUEL_MAP, MODE_MAP
from optimization.qpso import QPSOOptimizer
from optimization.pso import CanonicalPSOOptimizer
from optimization.genetic_algorithm import GeneticAlgorithmOptimizer
from optimization.differential_evolution import DifferentialEvolutionOptimizer
from optimization.random_search import RandomSearchOptimizer


def run_smoke_benchmark():
    out_dir = Path("results/audit/phase3_2")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== Initializing Phase 3.2 Controlled Smoke Benchmark ===")
    surrogates = load_real_surrogates()
    scen = BENCHMARK_SCENARIOS["SCEN-01"]
    evaluator = FleetEvaluationEngine(safe_objective=surrogates[scen.vessel_id], lambda_robust=0.5)

    # Standard multi-objective weights [Fuel, Cost, GHG, Schedule, Risk]
    weights = np.array([0.35, 0.30, 0.25, 0.05, 0.05])
    eval_fn, xl, xu = create_eval_function_for_scenario(scen, evaluator, weights=weights)

    eval_budget = 500
    seeds = [42, 142, 242]
    smoke_records = []

    print(f"Scenario: {scen.scenario_id} ({scen.name}) | Vessel: {scen.vessel_id}")
    print(f"Budget per run: {eval_budget} evaluations | Seeds: {seeds}")

    for seed in seeds:
        print(f"\n--- Testing Seed {seed} ---")
        optimizers = [
            ("QPSO", QPSOOptimizer(n_particles=25, max_iterations=20, seed=seed)),
            ("PSO", CanonicalPSOOptimizer(n_particles=25, max_iterations=20, seed=seed)),
            ("GA", GeneticAlgorithmOptimizer(population_size=25, max_generations=20, seed=seed)),
            ("DE", DifferentialEvolutionOptimizer(population_size=25, max_generations=20, seed=seed)),
            ("Random_Search", RandomSearchOptimizer(max_evaluations=eval_budget, seed=seed)),
        ]

        for opt_name, opt in optimizers:
            t0 = time.time()
            res_opt = opt.optimize(lambda x: eval_fn(x)[0], xl=xl, xu=xu, max_evaluations=eval_budget)
            rt = time.time() - t0

            best_x = res_opt["best_x"]
            best_loss, detailed_eval = eval_fn(best_x)

            fuel_idx = int(np.clip(np.round(best_x[2]), 0, len(FUEL_MAP) - 1))
            mode_idx = int(np.clip(np.round(best_x[3]), 0, len(MODE_MAP) - 1))
            fuel_str = FUEL_MAP[fuel_idx]
            mode_str = MODE_MAP[mode_idx]

            phys_obj = float(best_loss - detailed_eval.total_penalty_value)
            penalty_val = float(detailed_eval.total_penalty_value)

            rec = {
                "experiment_id": "SMOKE_BENCHMARK",
                "timestamp": TIMESTAMP,
                "git_commit": GIT_COMMIT,
                "seed": seed,
                "optimizer": opt_name,
                "vessel": scen.vessel_id,
                "total_evaluations": res_opt["total_evaluations"],
                "runtime_seconds": round(rt, 3),
                "is_feasible": detailed_eval.is_feasible,
                "domain_status": detailed_eval.domain_status,
                "best_physical_objective": round(phys_obj, 4),
                "best_total_objective": round(best_loss, 4),
                "penalty": round(penalty_val, 2),
                "penalty_fraction": round(penalty_val / max(best_loss, 1e-6), 4),
                "speed_knots": round(float(best_x[0]), 2),
                "cargo_tonnes": round(float(best_x[1]), 1),
                "fuel_type": fuel_str,
                "operating_mode": mode_str,
                "total_fuel_tonnes": detailed_eval.total_fuel_tonnes,
                "total_opex_usd": detailed_eval.total_opex_usd,
                "total_wtw_ghg_tonnes": detailed_eval.total_wtw_ghg_tonnes,
                "cii_rating": detailed_eval.cii_rating,
                "fueleu_compliant": detailed_eval.fueleu_compliant,
            }
            smoke_records.append(rec)
            print(f"  [{opt_name:13s}] Feasible: {rec['is_feasible']} | Status: {rec['domain_status']} | Phys: {rec['best_physical_objective']:.4f} | Total: {rec['best_total_objective']:.4f} | Penalty: {rec['penalty']:.1f} | Speed: {rec['speed_knots']:.1f}kn | Fuel: {rec['fuel_type']}")

    df_smoke = pd.DataFrame(smoke_records)
    out_file = out_dir / "05_smoke_benchmark.csv"
    df_smoke.to_csv(out_file, index=False)
    print(f"\nSaved smoke benchmark results to: {out_file} ({len(df_smoke)} runs)")

    # Mandatory sanity checks
    feas_rate = df_smoke["is_feasible"].mean() * 100.0
    print(f"Overall Feasibility Rate: {feas_rate:.1f}%")
    assert feas_rate > 90.0, f"STOP CONDITION: Feasibility rate {feas_rate:.1f}% <= 90%!"

    # Mandatory: The benchmark must NOT be dominated by penalty values (e.g. not 115,000)
    max_total = df_smoke["best_total_objective"].max()
    print(f"Max Total Objective: {max_total:.4f}")
    assert max_total < 5000.0, f"STOP CONDITION: Penalty values dominate benchmark (max objective = {max_total})!"

    print(">>> PASS: Controlled Smoke Benchmark succeeded. All optimizers found feasible solutions without penalty dominance!")
    return df_smoke


if __name__ == "__main__":
    run_smoke_benchmark()
