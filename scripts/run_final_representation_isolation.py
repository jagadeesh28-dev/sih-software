"""
SIH26138 Egreen Quanta — Pure Representation-Isolation Benchmark (C1 vs C2)
Isolates CATEGORICAL REPRESENTATION under strictly identical:
- Continuous search engine: Differential Evolution (DE/rand/1/bin, F=0.8, CR=0.9)
- Common C0 Hungarian / Greedy repair heuristic
- Deb's feasibility-first tournament selection
- Bounded Epsilon-Pareto archive
- Budget: Exactly 2,500 evaluations per run (50 pop x 50 iterations)
- 30 matched seeds: 1001 to 1030
- Canonical evaluator: CommonFleetEvaluator wrapping real FuelCast GBDT models

C1: Classical Discrete / Categorical Representation + Classical DE
C2: Q-Bit / Dirichlet-Q Probabilistic Representation + Classical DE
"""

import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd
from scipy import stats

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from optimization.fleet_evaluator_phase4 import Phase4FleetEvaluator
from experiments.exp_phase3_master_runner import load_real_surrogates
from src.evaluator.common_evaluator import CommonFleetEvaluator, EvaluationOutput
from src.representation.qbit_representation import QBit, DirichletQVector, ConditionalDemandObservation
from src.representation.repair import FleetSolutionRepairer
from src.benchmark.metrics import is_pareto_efficient, compute_2d_hypervolume

# Problem Dimensions and Settings
SEEDS = list(range(1001, 1031))
BUDGET = 2500
POP_SIZE = 50
MAX_GEN = 50
N_VESSELS = 3
DIM = 18

REF_POINTS = {
    "R1_nominal": np.array([500.0, 500000.0]),
    "R2_tighter": np.array([450.0, 450000.0]),
    "R3_expanded": np.array([600.0, 600000.0]),
    "R4_wide": np.array([1000.0, 1000000.0]),
}

CAT_DIMS = [0, 3, 4, 5, 6, 9, 10, 11, 12, 15, 16, 17]
CONT_DIMS = [1, 2, 7, 8, 13, 14]

COMP_MATRIX = np.array([
    [1.0, 0.0, 0.0],  # Poseidon: Demand-A
    [0.0, 1.0, 0.0],  # Triton: Demand-B
    [0.0, 0.0, 1.0],  # Ceto: Demand-C
])

def compute_categorical_entropy(pop: np.ndarray) -> float:
    """Computes mean Shannon entropy across discrete categorical dimensions."""
    entropies = []
    cat_vals = np.round(pop[:, CAT_DIMS]).astype(int)
    for col in range(cat_vals.shape[1]):
        _, counts = np.unique(cat_vals[:, col], return_counts=True)
        p = counts / np.sum(counts)
        entropies.append(-float(np.sum(p * np.log2(p + 1e-12))))
    return float(np.mean(entropies))

def run_c1_classical_de(seed: int, base_evaluator: Phase4FleetEvaluator, repairer: FleetSolutionRepairer) -> Dict[str, Any]:
    """
    C1: Classical Categorical Representation + Classical DE Continuous Optimizer.
    Categorical variables: classical discrete random initialization + DE mutation/crossover + C0 repair.
    Continuous variables: classical DE (F=0.8, CR=0.9).
    """
    t0 = time.perf_counter()
    rng = np.random.default_rng(seed)
    comm_eval = CommonFleetEvaluator(base_evaluator, max_budget=BUDGET)
    xl, xu = base_evaluator.get_bounds()

    # 1. Initialize population
    pop = np.zeros((POP_SIZE, DIM), dtype=float)
    for i in range(POP_SIZE):
        for v in range(N_VESSELS):
            off = v * 6
            pop[i, off + 0] = float(rng.integers(0, 4))                     # Demand: 0..3
            pop[i, off + 1] = float(rng.uniform(xl[off + 1], xu[off + 1]))  # Cargo
            pop[i, off + 2] = float(rng.uniform(xl[off + 2], xu[off + 2]))  # Speed
            pop[i, off + 3] = float(rng.integers(0, 5))                     # Fuel: 0..4
            pop[i, off + 4] = float(rng.integers(0, 4))                     # Mode: 0..3
            pop[i, off + 5] = float(rng.integers(0, 2))                     # Shore: 0..1

        pop[i], _, _ = repairer.repair_vector(pop[i])

    pop_outputs: List[Optional[EvaluationOutput]] = []
    pareto_archive: List[Tuple[np.ndarray, np.ndarray, EvaluationOutput]] = []
    unique_cat_configs = set()
    feas_count = 0
    entropy_history = []
    diversity_history = []

    for i in range(POP_SIZE):
        out = comm_eval.evaluate(pop[i])
        pop_outputs.append(out)
        unique_cat_configs.add(tuple(np.round(pop[i, CAT_DIMS]).astype(int)))
        if out.is_feasible:
            feas_count += 1
            pareto_archive.append((out.objectives[:2].copy(), pop[i].copy(), out))

    best_idx = 0
    for i in range(1, POP_SIZE):
        if CommonFleetEvaluator.deb_prefers(pop_outputs[i], pop_outputs[best_idx]):
            best_idx = i
    best_out = pop_outputs[best_idx]

    # 2. Main Generational DE Loop
    gen = 0
    f_mut = 0.8
    cr = 0.9

    while gen < MAX_GEN and comm_eval.evaluation_count < BUDGET:
        entropy_history.append(compute_categorical_entropy(pop))
        diversity_history.append(float(np.mean(np.std(pop[:, CONT_DIMS], axis=0))))

        for i in range(POP_SIZE):
            if comm_eval.evaluation_count >= BUDGET:
                break
            idxs = [idx for idx in range(POP_SIZE) if idx != i]
            r1, r2, r3 = rng.choice(idxs, size=3, replace=False)

            # Continuous difference vector mutation
            v_donor = pop[r1] + f_mut * (pop[r2] - pop[r3])
            v_donor = np.clip(v_donor, xl, xu)

            # Discrete rounding for categorical dimensions
            for d in CAT_DIMS:
                v_donor[d] = np.round(v_donor[d])

            # Binomial crossover
            j_rand = rng.integers(0, DIM)
            u = pop[i].copy()
            for d in range(DIM):
                if rng.uniform() <= cr or d == j_rand:
                    u[d] = v_donor[d]

            # Principled C0 repair
            u, was_rep, _ = repairer.repair_vector(u)
            out_u = comm_eval.evaluate(u)
            unique_cat_configs.add(tuple(np.round(u[CAT_DIMS]).astype(int)))

            if out_u.is_feasible:
                feas_count += 1
                pareto_archive.append((out_u.objectives[:2].copy(), u.copy(), out_u))

            # Deb's feasibility-first selection
            if CommonFleetEvaluator.deb_prefers(out_u, pop_outputs[i]):
                pop[i] = u.copy()
                pop_outputs[i] = out_u
                if CommonFleetEvaluator.deb_prefers(out_u, best_out):
                    best_out = out_u

        gen += 1

    t1 = time.perf_counter()

    # Pareto archiving & multi-reference HV
    hvs = {}
    non_dom_points = []
    if len(pareto_archive) > 0:
        pts = np.array([item[0] for item in pareto_archive])
        eff = is_pareto_efficient(pts)
        non_dom_points = pts[eff]
        for r_name, r_pt in REF_POINTS.items():
            hvs[r_name] = compute_2d_hypervolume(non_dom_points, r_pt)
    else:
        for r_name in REF_POINTS:
            hvs[r_name] = 0.0

    return {
        "algorithm": "C1_Classical_DE",
        "representation": "Classical_Categorical",
        "continuous_engine": "Differential_Evolution",
        "seed": seed,
        "runtime_seconds": round(t1 - t0, 4),
        "objective_evaluations": comm_eval.evaluation_count,
        "best_fitness": round(best_out.fitness, 4),
        "physical_objective": round(best_out.physical_fitness, 4),
        "penalty": round(best_out.penalty, 2),
        "is_feasible": bool(best_out.is_feasible),
        "run_feasibility": 1 if best_out.is_feasible else 0,
        "candidate_feasibility_rate": round(feas_count / max(1, comm_eval.evaluation_count) * 100.0, 2),
        "hv_nominal": round(hvs["R1_nominal"], 2),
        "hv_tighter": round(hvs["R2_tighter"], 2),
        "hv_expanded": round(hvs["R3_expanded"], 2),
        "hv_wide": round(hvs["R4_wide"], 2),
        "pareto_size": len(non_dom_points),
        "unique_cat_configs": len(unique_cat_configs),
        "duplicate_configs": comm_eval.evaluation_count - len(unique_cat_configs),
        "mean_cat_entropy": round(float(np.mean(entropy_history)) if entropy_history else 0.0, 4),
        "mean_pop_diversity": round(float(np.mean(diversity_history)) if diversity_history else 0.0, 4),
        "repair_count": repairer.total_repairs_count,
        "repair_rate": round(repairer.get_repair_rate(), 4),
        "non_dom_points": non_dom_points,
    }

def run_c2_qbit_de(seed: int, base_evaluator: Phase4FleetEvaluator, repairer: FleetSolutionRepairer) -> Dict[str, Any]:
    """
    C2: Q-Bit / Dirichlet-Q Probabilistic Categorical Representation + Classical DE Continuous Optimizer.
    Categorical variables: QBit, DirichletQVector, and ConditionalDemandObservation.
    Continuous variables: Classical DE (F=0.8, CR=0.9).
    Repair: identical C0 repair.
    Selection: identical Deb's rule + rotation toward improved solutions.
    """
    t0 = time.perf_counter()
    rng = np.random.default_rng(seed)
    comm_eval = CommonFleetEvaluator(base_evaluator, max_budget=BUDGET)
    xl, xu = base_evaluator.get_bounds()

    # 1. Initialize Quantum Probabilistic Representations per particle
    shore_qbits = [[QBit() for _ in range(N_VESSELS)] for _ in range(POP_SIZE)]
    fuel_qvectors = [[DirichletQVector(n_categories=5) for _ in range(N_VESSELS)] for _ in range(POP_SIZE)]
    mode_qvectors = [[DirichletQVector(n_categories=4) for _ in range(N_VESSELS)] for _ in range(POP_SIZE)]
    demand_q_obs = [ConditionalDemandObservation(n_vessels=N_VESSELS, n_demands=3) for _ in range(POP_SIZE)]

    pop = np.zeros((POP_SIZE, DIM), dtype=float)
    for i in range(POP_SIZE):
        dem_assigns = demand_q_obs[i].observe(COMP_MATRIX, rng=rng)
        for v in range(N_VESSELS):
            off = v * 6
            pop[i, off + 0] = float(dem_assigns[v])
            pop[i, off + 1] = float(rng.uniform(xl[off + 1], xu[off + 1]))  # Cargo
            pop[i, off + 2] = float(rng.uniform(xl[off + 2], xu[off + 2]))  # Speed
            pop[i, off + 3] = float(fuel_qvectors[i][v].measure(rng=rng))   # Fuel
            pop[i, off + 4] = float(mode_qvectors[i][v].measure(rng=rng))   # Mode
            pop[i, off + 5] = float(shore_qbits[i][v].measure(rng=rng))     # Shore

        pop[i], _, _ = repairer.repair_vector(pop[i])

    pop_outputs: List[Optional[EvaluationOutput]] = []
    pareto_archive: List[Tuple[np.ndarray, np.ndarray, EvaluationOutput]] = []
    unique_cat_configs = set()
    feas_count = 0
    entropy_history = []
    diversity_history = []

    for i in range(POP_SIZE):
        out = comm_eval.evaluate(pop[i])
        pop_outputs.append(out)
        unique_cat_configs.add(tuple(np.round(pop[i, CAT_DIMS]).astype(int)))
        if out.is_feasible:
            feas_count += 1
            pareto_archive.append((out.objectives[:2].copy(), pop[i].copy(), out))

    best_idx = 0
    for i in range(1, POP_SIZE):
        if CommonFleetEvaluator.deb_prefers(pop_outputs[i], pop_outputs[best_idx]):
            best_idx = i
    best_out = pop_outputs[best_idx]

    # 2. Main Generational Loop: Q-Bit Categorical + DE Continuous
    gen = 0
    f_mut = 0.8
    cr = 0.9
    rotation_step = 0.05 * np.pi

    while gen < MAX_GEN and comm_eval.evaluation_count < BUDGET:
        entropy_history.append(compute_categorical_entropy(pop))
        diversity_history.append(float(np.mean(np.std(pop[:, CONT_DIMS], axis=0))))

        for i in range(POP_SIZE):
            if comm_eval.evaluation_count >= BUDGET:
                break
            idxs = [idx for idx in range(POP_SIZE) if idx != i]
            r1, r2, r3 = rng.choice(idxs, size=3, replace=False)

            u = np.zeros(DIM, dtype=float)

            # 2A. Sample Categoricals from Q-Bit Superpositions
            dem_assigns = demand_q_obs[i].observe(COMP_MATRIX, rng=rng)
            for v in range(N_VESSELS):
                off = v * 6
                u[off + 0] = float(dem_assigns[v])
                u[off + 3] = float(fuel_qvectors[i][v].measure(rng=rng))
                u[off + 4] = float(mode_qvectors[i][v].measure(rng=rng))
                u[off + 5] = float(shore_qbits[i][v].measure(rng=rng))

            # 2B. Continuous Dimensions via Identical DE Mutation & Crossover
            for d in CONT_DIMS:
                v_cont = pop[r1, d] + f_mut * (pop[r2, d] - pop[r3, d])
                v_cont = np.clip(v_cont, xl[d], xu[d])
                if rng.uniform() <= cr:
                    u[d] = v_cont
                else:
                    u[d] = pop[i, d]

            # 2C. Principled C0 Repair
            u, was_rep, _ = repairer.repair_vector(u)
            out_u = comm_eval.evaluate(u)
            unique_cat_configs.add(tuple(np.round(u[CAT_DIMS]).astype(int)))

            if out_u.is_feasible:
                feas_count += 1
                pareto_archive.append((out_u.objectives[:2].copy(), u.copy(), out_u))

            # 2D. Deb's Selection & Quantum Unitary Gate Rotation
            if CommonFleetEvaluator.deb_prefers(out_u, pop_outputs[i]):
                pop[i] = u.copy()
                pop_outputs[i] = out_u

                # Unitary gate rotation toward improved state
                target_dems = np.array([int(round(u[v * 6])) for v in range(N_VESSELS)])
                demand_q_obs[i].update_toward(target_dems, step_size=rotation_step)
                for v in range(N_VESSELS):
                    fuel_qvectors[i][v].update(int(round(u[v * 6 + 3])))
                    mode_qvectors[i][v].update(int(round(u[v * 6 + 4])))
                    shore_qbits[i][v].rotate_toward(int(round(u[v * 6 + 5])), step_size=rotation_step)

                if CommonFleetEvaluator.deb_prefers(out_u, best_out):
                    best_out = out_u

        gen += 1

    t1 = time.perf_counter()

    # Pareto archiving & multi-reference HV
    hvs = {}
    non_dom_points = []
    if len(pareto_archive) > 0:
        pts = np.array([item[0] for item in pareto_archive])
        eff = is_pareto_efficient(pts)
        non_dom_points = pts[eff]
        for r_name, r_pt in REF_POINTS.items():
            hvs[r_name] = compute_2d_hypervolume(non_dom_points, r_pt)
    else:
        for r_name in REF_POINTS:
            hvs[r_name] = 0.0

    return {
        "algorithm": "C2_QBit_DE",
        "representation": "QBit_Probabilistic",
        "continuous_engine": "Differential_Evolution",
        "seed": seed,
        "runtime_seconds": round(t1 - t0, 4),
        "objective_evaluations": comm_eval.evaluation_count,
        "best_fitness": round(best_out.fitness, 4),
        "physical_objective": round(best_out.physical_fitness, 4),
        "penalty": round(best_out.penalty, 2),
        "is_feasible": bool(best_out.is_feasible),
        "run_feasibility": 1 if best_out.is_feasible else 0,
        "candidate_feasibility_rate": round(feas_count / max(1, comm_eval.evaluation_count) * 100.0, 2),
        "hv_nominal": round(hvs["R1_nominal"], 2),
        "hv_tighter": round(hvs["R2_tighter"], 2),
        "hv_expanded": round(hvs["R3_expanded"], 2),
        "hv_wide": round(hvs["R4_wide"], 2),
        "pareto_size": len(non_dom_points),
        "unique_cat_configs": len(unique_cat_configs),
        "duplicate_configs": comm_eval.evaluation_count - len(unique_cat_configs),
        "mean_cat_entropy": round(float(np.mean(entropy_history)) if entropy_history else 0.0, 4),
        "mean_pop_diversity": round(float(np.mean(diversity_history)) if diversity_history else 0.0, 4),
        "repair_count": repairer.total_repairs_count,
        "repair_rate": round(repairer.get_repair_rate(), 4),
        "non_dom_points": non_dom_points,
    }

def main():
    print("=== SIH26138 PURE REPRESENTATION-ISOLATION EXPERIMENT (C1 vs C2) ===")
    print("Initializing real surrogate models and common evaluator...")
    surrogates = load_real_surrogates()
    base_evaluator = Phase4FleetEvaluator(surrogates=surrogates, lambda_robust=0.50)
    repairer = FleetSolutionRepairer()

    c1_results = []
    c2_results = []

    print(f"Executing 30 matched seeds ({SEEDS[0]}..{SEEDS[-1]}) for C1 (Classical Categorical + DE)...")
    for s in SEEDS:
        res = run_c1_classical_de(s, base_evaluator, repairer)
        c1_results.append(res)
        print(f"  [C1] Seed {s}: Phys={res['physical_objective']:.4f}, Feas={res['candidate_feasibility_rate']}%, CatEntropy={res['mean_cat_entropy']:.4f}, HV={res['hv_nominal']/1e6:.2f}M, Time={res['runtime_seconds']:.2f}s")

    print(f"\nExecuting 30 matched seeds ({SEEDS[0]}..{SEEDS[-1]}) for C2 (Q-Bit Categorical + DE)...")
    for s in SEEDS:
        res = run_c2_qbit_de(s, base_evaluator, repairer)
        c2_results.append(res)
        print(f"  [C2] Seed {s}: Phys={res['physical_objective']:.4f}, Feas={res['candidate_feasibility_rate']}%, CatEntropy={res['mean_cat_entropy']:.4f}, HV={res['hv_nominal']/1e6:.2f}M, Time={res['runtime_seconds']:.2f}s")

    # Combine into pooled reference front for IGD+ calculation
    all_pareto_pts = []
    for r in c1_results + c2_results:
        if len(r["non_dom_points"]) > 0:
            all_pareto_pts.append(r["non_dom_points"])

    if len(all_pareto_pts) > 0:
        pooled_pts = np.vstack(all_pareto_pts)
        eff_pooled = is_pareto_efficient(pooled_pts)
        ref_front = pooled_pts[eff_pooled]
        # Normalize ref front for fair IGD+
        f_min = np.min(ref_front, axis=0)
        f_max = np.max(ref_front, axis=0) + 1e-9
        norm_ref = (ref_front - f_min) / (f_max - f_min)
    else:
        norm_ref = None

    def calc_igd_plus(pts: np.ndarray) -> float:
        if norm_ref is None or len(pts) == 0:
            return 1.0
        norm_pts = (pts - f_min) / (f_max - f_min)
        # For each point in ref_front, find min distance to any point in archive (modified distance max(a - r, 0))
        dists = []
        for r_pt in norm_ref:
            # Modified distance vector: max(a_m - r_m, 0)
            diff = np.maximum(norm_pts - r_pt, 0.0)
            d = np.min(np.sqrt(np.sum(diff ** 2, axis=1)))
            dists.append(d)
        return float(np.mean(dists))

    for r in c1_results:
        r["igd_plus"] = round(calc_igd_plus(r["non_dom_points"]), 5)
    for r in c2_results:
        r["igd_plus"] = round(calc_igd_plus(r["non_dom_points"]), 5)

    # Convert to DataFrames
    cols_to_drop = ["non_dom_points"]
    df_c1 = pd.DataFrame([{k: v for k, v in r.items() if k not in cols_to_drop} for r in c1_results])
    df_c2 = pd.DataFrame([{k: v for k, v in r.items() if k not in cols_to_drop} for r in c2_results])
    df_both = pd.concat([df_c1, df_c2], ignore_index=True)

    # Save raw benchmark results
    out_dir_raw = repo_root / "results" / "raw"
    out_dir_raw.mkdir(parents=True, exist_ok=True)
    df_both.to_csv(out_dir_raw / "final_representation_benchmark.csv", index=False)
    print(f"\nSaved raw representation benchmark to {out_dir_raw / 'final_representation_benchmark.csv'}")

    # Summary table
    metrics_to_summarize = [
        "run_feasibility", "candidate_feasibility_rate", "physical_objective",
        "hv_nominal", "hv_tighter", "hv_expanded", "hv_wide",
        "igd_plus", "pareto_size", "unique_cat_configs", "mean_cat_entropy",
        "mean_pop_diversity", "repair_rate", "runtime_seconds"
    ]

    summary_rows = []
    stat_rows = []

    # Bootstrap 95% CI helper
    def bootstrap_ci(arr: np.ndarray, n_boot: int = 10000) -> Tuple[float, float]:
        rng_boot = np.random.default_rng(42)
        boots = [np.mean(rng_boot.choice(arr, size=len(arr), replace=True)) for _ in range(n_boot)]
        return float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))

    # Hodges-Lehmann median difference estimator
    def hodges_lehmann(diff: np.ndarray) -> float:
        walsh_averages = [(diff[i] + diff[j]) / 2.0 for i in range(len(diff)) for j in range(i, len(diff))]
        return float(np.median(walsh_averages))

    for m in metrics_to_summarize:
        c1_vals = df_c1[m].to_numpy(dtype=float)
        c2_vals = df_c2[m].to_numpy(dtype=float)

        c1_mean, c1_sd = np.mean(c1_vals), np.std(c1_vals, ddof=1)
        c2_mean, c2_sd = np.mean(c2_vals), np.std(c2_vals, ddof=1)
        c1_med, c1_iqr = np.median(c1_vals), stats.iqr(c1_vals)
        c2_med, c2_iqr = np.median(c2_vals), stats.iqr(c2_vals)

        diff = c2_vals - c1_vals  # Positive means C2 > C1
        mean_diff = float(np.mean(diff))
        sd_diff = float(np.std(diff, ddof=1))
        med_diff = float(np.median(diff))
        iqr_diff = float(stats.iqr(diff))
        hl_diff = hodges_lehmann(diff)
        ci_low, ci_high = bootstrap_ci(diff)

        # Wilcoxon signed-rank test
        try:
            w_stat, p_val = stats.wilcoxon(c2_vals, c1_vals, zero_method="wilcox", alternative="two-sided")
            # Rank-biserial correlation effect size r = W / max_W
            n = len(diff)
            r_biserial = float(1.0 - (2.0 * w_stat) / (n * (n + 1) / 2.0))
        except Exception:
            w_stat, p_val, r_biserial = 0.0, 1.0, 0.0

        summary_rows.append({
            "metric": m,
            "C1_Classical_Mean": round(c1_mean, 4),
            "C1_Classical_SD": round(c1_sd, 4),
            "C1_Classical_Median": round(c1_med, 4),
            "C1_Classical_IQR": round(c1_iqr, 4),
            "C2_QBit_Mean": round(c2_mean, 4),
            "C2_QBit_SD": round(c2_sd, 4),
            "C2_QBit_Median": round(c2_med, 4),
            "C2_QBit_IQR": round(c2_iqr, 4),
            "Mean_Difference (C2-C1)": round(mean_diff, 4),
            "Hodges_Lehmann_Difference": round(hl_diff, 4),
            "Bootstrap_95_CI_Low": round(ci_low, 4),
            "Bootstrap_95_CI_High": round(ci_high, 4),
            "Wilcoxon_W": round(w_stat, 2),
            "Wilcoxon_p": p_val,
            "Rank_Biserial_Effect_Size": round(r_biserial, 4),
        })

    df_summary = pd.DataFrame(summary_rows)

    # Holm-Bonferroni correction on p-values
    p_vals = df_summary["Wilcoxon_p"].tolist()
    m_tests = len(p_vals)
    sorted_indices = np.argsort(p_vals)
    holm_p = np.zeros(m_tests)
    for rank, idx in enumerate(sorted_indices):
        holm_p[idx] = min(1.0, p_vals[idx] * (m_tests - rank))
    df_summary["Holm_Bonferroni_p"] = np.round(holm_p, 5)

    def interpret_result(row):
        p_raw = row["Wilcoxon_p"]
        p_holm = row["Holm_Bonferroni_p"]
        eff = abs(row["Rank_Biserial_Effect_Size"])
        if p_holm < 0.05:
            if eff >= 0.30:
                return "SIGNIFICANT + PRACTICALLY MEANINGFUL"
            else:
                return "SIGNIFICANT BUT PRACTICALLY SMALL"
        elif p_raw < 0.05:
            return "SIGNIFICANT UNCORRECTED (INCONCLUSIVE)"
        else:
            return "NOT SIGNIFICANT"

    df_summary["Interpretation"] = df_summary.apply(interpret_result, axis=1)

    # Save summary tables and statistics
    out_dir_tables = repo_root / "results" / "tables"
    out_dir_tables.mkdir(parents=True, exist_ok=True)
    df_summary.to_csv(out_dir_tables / "final_representation_comparison.csv", index=False)

    out_dir_stats = repo_root / "results" / "statistics"
    out_dir_stats.mkdir(parents=True, exist_ok=True)
    df_summary.to_csv(out_dir_stats / "final_representation_statistics.csv", index=False)

    print(f"Saved comparison table to {out_dir_tables / 'final_representation_comparison.csv'}")
    print(f"Saved statistics to {out_dir_stats / 'final_representation_statistics.csv'}")

    print("\n=== FINAL REPRESENTATION ISOLATION SUMMARY TABLE ===")
    print(df_summary[["metric", "C1_Classical_Mean", "C2_QBit_Mean", "Mean_Difference (C2-C1)", "Wilcoxon_p", "Holm_Bonferroni_p", "Interpretation"]].to_string())

if __name__ == "__main__":
    main()
