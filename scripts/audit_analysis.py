import os
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy import stats

base_dir = str(Path(__file__).resolve().parents[1] / "PHASE5")
res_dir = os.path.join(base_dir, "results")
val_dir = os.path.join(base_dir, "validation")

algos = ["A0", "A1", "A2", "A3", "A4", "A5", "DE", "PSO", "GA", "Random", "NSGA3"]
dfs = {a: pd.read_csv(os.path.join(res_dir, f"{a}.csv")) for a in algos}

print("=== RAW ALGORITHM METRICS RECOMPUTATION ===")
recomputed_summary = []
for a in algos:
    df = dfs[a]
    n = len(df)
    feas_n = int(df["is_feasible"].sum())
    feas_rate = float(df["is_feasible"].mean() * 100.0)
    mean_fit = float(df["best_fitness"].mean())
    med_fit = float(df["best_fitness"].median())
    p10_fit = float(np.percentile(df["best_fitness"], 10))
    std_fit = float(df["best_fitness"].std())
    mean_phys = float(df["physical_objective"].mean())
    mean_pen = float(df["penalty"].mean())
    first_feas = float(df["first_feasible_eval"].mean())
    runtime = float(df["runtime_seconds"].mean())
    repair_rate = float(df["repair_rate"].mean()) if "repair_rate" in df.columns else 0.0
    hv = float(df["pareto_hypervolume"].mean()) if "pareto_hypervolume" in df.columns else 0.0
    
    recomputed_summary.append({
        "algorithm": a,
        "n_runs": n,
        "feas_runs": feas_n,
        "feasibility_pct": feas_rate,
        "mean_fitness": mean_fit,
        "median_fitness": med_fit,
        "p10_fitness": p10_fit,
        "std_fitness": std_fit,
        "mean_physical": mean_phys,
        "mean_penalty": mean_pen,
        "first_feas_eval": first_feas,
        "runtime_s": runtime,
        "repair_rate_pct": repair_rate,
        "hypervolume": hv
    })
    print(f"{a:8s}: Feas={feas_rate:5.1f}% ({feas_n:2d}/{n:2d}) | MeanFit={mean_fit:10.2f} | MedFit={med_fit:8.2f} | MeanPhys={mean_phys:7.2f} | MeanPen={mean_pen:10.2f} | Runtime={runtime:5.2f}s | HV={hv:12.2f}")

print("\n=== COMPARISON WITH A5_ABLATION_TABLE.csv ===")
abl_df = pd.read_csv(os.path.join(res_dir, "A5_ABLATION_TABLE.csv"))
print(abl_df.to_string(index=False))

print("\n=== STATISTICAL RECALCULATION ===")
pairs = [
    ("A5", "A0"),
    ("A5", "A1"),
    ("A5", "DE"),
    ("A5", "PSO"),
    ("A5", "GA"),
    ("A5", "Random"),
    ("DE", "A0"),
]

stat_rows = []
for a_name, b_name in pairs:
    a_vals = dfs[a_name]["best_fitness"].values
    b_vals = dfs[b_name]["best_fitness"].values
    diff = a_vals - b_vals
    mean_d = float(np.mean(diff))
    
    # Wilcoxon signed-rank test
    # Check Pratt vs Wilcox treatment of zeros
    non_zero = diff[np.abs(diff) > 1e-5]
    if len(non_zero) > 0:
        w_stat, w_pval = stats.wilcoxon(diff, zero_method="pratt")
    else:
        w_stat, w_pval = 0.0, 1.0
        
    # Permutation test (paired)
    n_perm = 100000
    observed_diff = np.mean(diff)
    signs = np.random.choice([-1, 1], size=(n_perm, len(diff)))
    perm_means = np.mean(diff * signs, axis=1)
    perm_p = float(np.mean(np.abs(perm_means) >= np.abs(observed_diff)))
    
    # Hodges-Lehmann difference
    pairwise_diffs = []
    for i in range(len(diff)):
        for j in range(i, len(diff)):
            pairwise_diffs.append((diff[i] + diff[j]) / 2.0)
    hl_diff = float(np.median(pairwise_diffs))
    
    # Bootstrap CI
    n_boot = 10000
    boot_means = []
    for _ in range(n_boot):
        sample = np.random.choice(diff, size=len(diff), replace=True)
        boot_means.append(np.mean(sample))
    ci_lower = float(np.percentile(boot_means, 2.5))
    ci_upper = float(np.percentile(boot_means, 97.5))
    
    # Rank-biserial effect size
    if len(non_zero) > 0:
        ranks = stats.rankdata(np.abs(non_zero))
        pos_sum = np.sum(ranks[non_zero > 0])
        neg_sum = np.sum(ranks[non_zero < 0])
        total_sum = pos_sum + neg_sum
        r_effect = float((pos_sum - neg_sum) / total_sum) if total_sum > 0 else 0.0
    else:
        r_effect = 0.0
        
    stat_rows.append({
        "pair": f"{a_name}_vs_{b_name}",
        "mean_diff": mean_d,
        "wilcoxon_p": float(w_pval),
        "permutation_p": perm_p,
        "rank_biserial": r_effect,
        "hodges_lehmann": hl_diff,
        "boot_ci_lower": ci_lower,
        "boot_ci_upper": ci_upper
    })
    print(f"{a_name}_vs_{b_name:6s}: MeanDiff={mean_d:10.2f}, WilcP={w_pval:.5e}, PermP={perm_p:.5e}, HL={hl_diff:10.2f}, CI=[{ci_lower:.2f}, {ci_upper:.2f}], r={r_effect:+.4f}")

# Save recomputed statistics
pd.DataFrame(stat_rows).to_csv(os.path.join(base_dir, "final_audit", "statistical_recalculation.csv"), index=False)
print("\nSaved statistical_recalculation.csv")
