"""
Parameter Tuning & Freezing Protocol:
Evaluates parameter stability on independent tuning seeds 2001-2010 and validation seeds 3001-3010.
Freezes parameters permanently before running the final matched benchmark (1001-1030).
"""

import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(".").resolve()))

from common.logger import setup_logger
from optimization.fleet_evaluator_phase4 import Phase4FleetEvaluator
from experiments.exp_phase3_master_runner import load_real_surrogates
from src.evaluator.common_evaluator import CommonFleetEvaluator
from src.algorithms.hybrid_qi import A5CompleteHybridQIOptimizer

logger = setup_logger("tuning_protocol")


def run_tuning():
    logger.info("Executing Parameter Tuning on independent seeds 2001-2010...")
    surrogates = load_real_surrogates()
    evaluator = Phase4FleetEvaluator(surrogates=surrogates, lambda_robust=0.50)
    xl, xu = evaluator.get_bounds()

    tuning_seeds = list(range(2001, 2011))
    validation_seeds = list(range(3001, 3011))

    # Parameter grid for A5:
    # beta_schedule in [(1.0, 0.5), (0.9, 0.4)], rotation_step in [0.03*pi, 0.05*pi, 0.08*pi]
    grid = [
        {"beta_start": 1.0, "beta_end": 0.5, "rotation_step": 0.05 * np.pi, "name": "Config_Default"},
        {"beta_start": 0.9, "beta_end": 0.4, "rotation_step": 0.05 * np.pi, "name": "Config_LowBeta"},
        {"beta_start": 1.0, "beta_end": 0.5, "rotation_step": 0.08 * np.pi, "name": "Config_HighRotation"},
    ]

    tuning_results = []
    for cfg in grid:
        scores = []
        feas_count = 0
        for s in tuning_seeds:
            comm = CommonFleetEvaluator(evaluator, max_budget=2500)
            opt = A5CompleteHybridQIOptimizer(
                seed=s,
                n_particles=50,
                max_iterations=50,
                beta_start=cfg["beta_start"],
                beta_end=cfg["beta_end"],
                rotation_step=cfg["rotation_step"],
            )
            res = opt.optimize(comm, xl, xu, budget=2500)
            scores.append(res.best_physical_objective if res.feasible_at_end else res.best_fitness)
            if res.feasible_at_end:
                feas_count += 1

        tuning_results.append({
            "config": cfg["name"],
            "beta_start": cfg["beta_start"],
            "beta_end": cfg["beta_end"],
            "rotation_step": cfg["rotation_step"],
            "feasibility_rate": (feas_count / len(tuning_seeds)) * 100.0,
            "mean_objective": float(np.mean(scores)),
            "std_objective": float(np.std(scores)),
        })

    df_tune = pd.DataFrame(tuning_results)
    logger.info("\nTuning Results (Seeds 2001-2010):\n" + df_tune.to_string())

    # Select best configuration (lowest mean objective with 100% feasibility)
    best_cfg = df_tune.sort_values(by=["feasibility_rate", "mean_objective"], ascending=[False, True]).iloc[0]
    logger.info(f"Selected Configuration: {best_cfg['config']}")

    # Validate on seeds 3001-3010
    logger.info("Validating Selected Configuration on validation seeds 3001-3010...")
    val_scores = []
    val_feas = 0
    for s in validation_seeds:
        comm = CommonFleetEvaluator(evaluator, max_budget=2500)
        opt = A5CompleteHybridQIOptimizer(
            seed=s,
            n_particles=50,
            max_iterations=50,
            beta_start=best_cfg["beta_start"],
            beta_end=best_cfg["beta_end"],
            rotation_step=best_cfg["rotation_step"],
        )
        res = opt.optimize(comm, xl, xu, budget=2500)
        val_scores.append(res.best_physical_objective if res.feasible_at_end else res.best_fitness)
        if res.feasible_at_end:
            val_feas += 1

    val_feas_rate = (val_feas / len(validation_seeds)) * 100.0
    val_mean_obj = float(np.mean(val_scores))
    logger.info(f"Validation Feasibility: {val_feas_rate:.1f}%, Mean Objective: {val_mean_obj:.4f}")

    # Freeze configuration permanently
    config_path = Path("configs") / "phase5_parameters.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    frozen_manifest = {
        "frozen_timestamp": pd.Timestamp.now().isoformat(),
        "tuning_seeds": tuning_seeds,
        "validation_seeds": validation_seeds,
        "final_benchmark_seeds": list(range(1001, 1031)),
        "evaluation_budget": 2500,
        "selected_parameters": {
            "n_particles": 50,
            "max_iterations": 50,
            "beta_start": float(best_cfg["beta_start"]),
            "beta_end": float(best_cfg["beta_end"]),
            "rotation_step": float(best_cfg["rotation_step"]),
            "crossover_rate": 0.9,
            "mutation_rate": 0.1,
            "f_mut": 0.8,
            "cr": 0.9,
        },
        "status": "FROZEN",
    }
    with open(config_path, "w") as f:
        json.dump(frozen_manifest, f, indent=2)

    logger.info(f"Parameters permanently FROZEN to {config_path}")


if __name__ == "__main__":
    run_tuning()
