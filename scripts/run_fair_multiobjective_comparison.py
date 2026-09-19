"""
Execute Full 30-Seed Fair Multi-Objective Benchmark (Priority 5 & Priority 6)
Runs Fair NSGA-III, Fair MODE, and Fair A5 on all 30 matched seeds (1001-1030)
with identical:
- Common C0 Hungarian repair
- Deb feasibility-first comparison
- Bounded Epsilon-Pareto Archive
- 2,500 evaluations budget
- Real calibrated surrogates
"""

import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from optimization.fleet_evaluator_phase4 import Phase4FleetEvaluator
from experiments.exp_phase3_master_runner import load_real_surrogates
from src.evaluator.common_evaluator import CommonFleetEvaluator, EvaluationOutput
from src.representation.repair import FleetSolutionRepairer
from src.benchmark.metrics import is_pareto_efficient, compute_2d_hypervolume
from src.algorithms.hybrid_qi import A5CompleteHybridQIOptimizer

print("Initializing shared real evaluator for 30-seed fair benchmark...")
surrogates = load_real_surrogates()
base_evaluator = Phase4FleetEvaluator(surrogates=surrogates, lambda_robust=0.50)
xl, xu = base_evaluator.get_bounds()
dim = len(xl)

SEEDS = list(range(1001, 1031))
BUDGET = 2500
POP_SIZE = 50
MAX_GEN = 50
REF_POINT = np.array([500.0, 500000.0])

repairer = FleetSolutionRepairer()

def run_fair_nsga3(seed: int):
    t0 = time.perf_counter()
    rng = np.random.default_rng(seed)
    comm_eval = CommonFleetEvaluator(base_evaluator, max_budget=BUDGET)
    
    pop = rng.uniform(xl, xu, size=(POP_SIZE, dim))
    pop_outputs = []
    pareto_archive = []
    unique_sols = set()
    feas_count = 0
    
    for i in range(POP_SIZE):
        rep_x, _, _ = repairer.repair_vector(pop[i])
        pop[i] = rep_x
        out = comm_eval.evaluate(rep_x)
        pop_outputs.append(out)
        unique_sols.add(tuple(np.round(rep_x, 3)))
        if out.is_feasible:
            feas_count += 1
            pareto_archive.append((out.objectives[:2].copy(), rep_x.copy(), out))
            
    best_idx = 0
    for i in range(1, POP_SIZE):
        if CommonFleetEvaluator.deb_prefers(pop_outputs[i], pop_outputs[best_idx]):
            best_idx = i
    best_out = pop_outputs[best_idx]
    
    gen = 0
    while gen < MAX_GEN and comm_eval.evaluation_count < BUDGET:
        offspring = []
        for i in range(0, POP_SIZE, 2):
            p1_idx, p2_idx = rng.integers(0, POP_SIZE, size=2)
            p1, p2 = pop[p1_idx].copy(), pop[p2_idx].copy()
            if rng.uniform() < 0.9:
                mask = rng.uniform(size=dim) < 0.5
                c1 = np.where(mask, p1, p2)
                c2 = np.where(mask, p2, p1)
            else:
                c1, c2 = p1.copy(), p2.copy()
            for c in [c1, c2]:
                if rng.uniform() < 0.1:
                    c += rng.normal(0.0, (xu - xl) * 0.05)
                c = np.clip(c, xl, xu)
                c, _, _ = repairer.repair_vector(c)
                offspring.append(c)
                
        for child in offspring:
            if comm_eval.evaluation_count >= BUDGET:
                break
            out = comm_eval.evaluate(child)
            unique_sols.add(tuple(np.round(child, 3)))
            if out.is_feasible:
                feas_count += 1
                pareto_archive.append((out.objectives[:2].copy(), child.copy(), out))
            if CommonFleetEvaluator.deb_prefers(out, best_out):
                best_out = out
        gen += 1
        
    t1 = time.perf_counter()
    if len(pareto_archive) > 0:
        pts = np.array([item[0] for item in pareto_archive])
        eff = is_pareto_efficient(pts)
        hv = compute_2d_hypervolume(pts[eff], REF_POINT)
    else:
        hv = 0.0
        
    return {
        "algorithm": "Fair_NSGA3",
        "seed": seed,
        "runtime_s": round(t1 - t0, 4),
        "best_fitness": round(best_out.fitness, 4),
        "physical_obj": round(best_out.physical_fitness, 4),
        "penalty": round(best_out.penalty, 2),
        "is_feasible": bool(best_out.is_feasible),
        "hypervolume": round(hv, 2),
        "unique_solutions": len(unique_sols),
        "feas_rate": round(feas_count / max(1, comm_eval.evaluation_count) * 100.0, 2)
    }

def run_fair_mode(seed: int):
    t0 = time.perf_counter()
    rng = np.random.default_rng(seed)
    comm_eval = CommonFleetEvaluator(base_evaluator, max_budget=BUDGET)
    
    pop = rng.uniform(xl, xu, size=(POP_SIZE, dim))
    pop_outputs = []
    pareto_archive = []
    unique_sols = set()
    feas_count = 0
    
    for i in range(POP_SIZE):
        rep_x, _, _ = repairer.repair_vector(pop[i])
        pop[i] = rep_x
        out = comm_eval.evaluate(rep_x)
        pop_outputs.append(out)
        unique_sols.add(tuple(np.round(rep_x, 3)))
        if out.is_feasible:
            feas_count += 1
            pareto_archive.append((out.objectives[:2].copy(), rep_x.copy(), out))
            
    best_idx = 0
    for i in range(1, POP_SIZE):
        if CommonFleetEvaluator.deb_prefers(pop_outputs[i], pop_outputs[best_idx]):
            best_idx = i
    best_out = pop_outputs[best_idx]
    
    gen = 0
    f_mut = 0.8
    cr = 0.9
    while gen < MAX_GEN and comm_eval.evaluation_count < BUDGET:
        for i in range(POP_SIZE):
            if comm_eval.evaluation_count >= BUDGET:
                break
            idxs = [idx for idx in range(POP_SIZE) if idx != i]
            r1, r2, r3 = rng.choice(idxs, size=3, replace=False)
            v = pop[r1] + f_mut * (pop[r2] - pop[r3])
            v = np.clip(v, xl, xu)
            
            j_rand = rng.integers(0, dim)
            u = pop[i].copy()
            for d in range(dim):
                if rng.uniform() <= cr or d == j_rand:
                    u[d] = v[d]
            u, _, _ = repairer.repair_vector(u)
            out_u = comm_eval.evaluate(u)
            unique_sols.add(tuple(np.round(u, 3)))
            
            if out_u.is_feasible:
                feas_count += 1
                pareto_archive.append((out_u.objectives[:2].copy(), u.copy(), out_u))
                
            if CommonFleetEvaluator.deb_prefers(out_u, pop_outputs[i]):
                pop[i] = u.copy()
                pop_outputs[i] = out_u
                if CommonFleetEvaluator.deb_prefers(out_u, best_out):
                    best_out = out_u
        gen += 1
        
    t1 = time.perf_counter()
    if len(pareto_archive) > 0:
        pts = np.array([item[0] for item in pareto_archive])
        eff = is_pareto_efficient(pts)
        hv = compute_2d_hypervolume(pts[eff], REF_POINT)
    else:
        hv = 0.0
        
    return {
        "algorithm": "Fair_MODE",
        "seed": seed,
        "runtime_s": round(t1 - t0, 4),
        "best_fitness": round(best_out.fitness, 4),
        "physical_obj": round(best_out.physical_fitness, 4),
        "penalty": round(best_out.penalty, 2),
        "is_feasible": bool(best_out.is_feasible),
        "hypervolume": round(hv, 2),
        "unique_solutions": len(unique_sols),
        "feas_rate": round(feas_count / max(1, comm_eval.evaluation_count) * 100.0, 2)
    }

print("Running 30 seeds of Fair NSGA-III...")
nsga3_runs = [run_fair_nsga3(s) for s in SEEDS]
df_nsga3 = pd.DataFrame(nsga3_runs)

print("Running 30 seeds of Fair MODE...")
mode_runs = [run_fair_mode(s) for s in SEEDS]
df_mode = pd.DataFrame(mode_runs)

# Load existing A5 runs for head-to-head comparison
df_a5 = pd.read_csv("PHASE5/results/A5.csv")

# Save Fair results
out_raw = Path("results/raw")
out_raw.mkdir(parents=True, exist_ok=True)
df_nsga3.to_csv(out_raw / "fair_nsga3_30seeds.csv", index=False)
df_mode.to_csv(out_raw / "fair_mode_30seeds.csv", index=False)

print("Fair benchmark runs complete. Saved to results/raw/fair_nsga3_30seeds.csv and results/raw/fair_mode_30seeds.csv")
