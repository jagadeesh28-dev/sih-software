import sys
from pathlib import Path
import pandas as pd
import numpy as np

repo_root = Path(".").resolve()
sys.path.insert(0, str(repo_root))

from experiments.exp_phase3_master_runner import load_real_surrogates, BENCHMARK_SCENARIOS, create_eval_function_for_scenario
from optimization.evaluator import FleetEvaluationEngine
from optimization.variables import SolutionChromosome, VesselAssignmentDecision

surrogates = load_real_surrogates()

for sc_id, scen in BENCHMARK_SCENARIOS.items():
    v_id = scen.vessel_id
    if v_id not in surrogates:
        continue
    safe_obj = surrogates[v_id]
    evaluator = FleetEvaluationEngine(safe_objective=safe_obj, lambda_robust=0.5)
    eval_fn, xl, xu = create_eval_function_for_scenario(scen, evaluator, evaluator.weights)
    
    # Mid-range test point: speed = design speed, cargo = 0, fuel = bio_methanol (2.0) or VLSFO (0.0), mode = 0, shore = 1
    spd = 18.0 if "poseidon" in v_id.lower() else (14.0 if "triton" in v_id.lower() else 10.0)
    # Bio-methanol
    x_test = np.array([spd, 0.0, 2.0, 0.0, 1.0])
    loss, res = eval_fn(x_test)
    print(f"[{sc_id}] Vessel: {v_id} | Speed: {spd:.1f} kn | Feasible: {res.is_feasible} | Domain: {res.domain_status} | Penalty: {res.total_penalty_value:.2f} | Fitness: {loss:.4f} | Hard: {res.hard_violations} | Soft: {res.soft_penalties}")
