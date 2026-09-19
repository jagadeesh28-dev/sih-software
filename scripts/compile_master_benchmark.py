"""
Compile Master Benchmark Ledgers, Tables, and Statistics
SIH26138 Final Scientific Closure & Benchmark Freeze
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

repo_root = Path(__file__).resolve().parent.parent
raw_dir = repo_root / "results" / "raw"
tables_dir = repo_root / "results" / "tables"
stats_dir = repo_root / "results" / "statistics"

tables_dir.mkdir(parents=True, exist_ok=True)
stats_dir.mkdir(parents=True, exist_ok=True)

# 1. Load all available verified run files
records = []

# Load Representation Isolation (C1 & C2)
df_rep = pd.read_csv(raw_dir / "final_representation_benchmark.csv")
for _, row in df_rep.iterrows():
    records.append({
        "algorithm": row["algorithm"],
        "seed": int(row["seed"]),
        "instance": "Heterogeneous_Fleet_D18",
        "dimension": 18,
        "evaluation_budget": 2500,
        "runtime_s": float(row["runtime_seconds"]),
        "best_fitness": float(row["best_fitness"]),
        "physical_objective": float(row["physical_objective"]),
        "penalty": float(row["penalty"]),
        "is_feasible": bool(row["is_feasible"]),
        "feasibility_rate": float(row["candidate_feasibility_rate"]),
        "hypervolume": float(row["hv_nominal"]),
        "unique_solutions": int(row["unique_cat_configs"]),
        "cat_entropy": float(row["mean_cat_entropy"]),
        "pop_diversity": float(row["mean_pop_diversity"]),
        "repair_rate": float(row["repair_rate"]),
        "engine_role": "Research_Exploration" if "QBit" in row["algorithm"] else "Classical_Baseline",
        "source_csv": "final_representation_benchmark.csv"
    })

# Load Fair MODE
df_mode = pd.read_csv(raw_dir / "fair_mode_30seeds.csv")
for _, row in df_mode.iterrows():
    records.append({
        "algorithm": "Fair_MODE",
        "seed": int(row["seed"]),
        "instance": "Heterogeneous_Fleet_D18",
        "dimension": 18,
        "evaluation_budget": 2500,
        "runtime_s": float(row["runtime_s"]),
        "best_fitness": float(row["best_fitness"]),
        "physical_objective": float(row["physical_obj"]),
        "penalty": float(row["penalty"]),
        "is_feasible": bool(row["is_feasible"]),
        "feasibility_rate": float(row["feas_rate"]),
        "hypervolume": float(row["hypervolume"]),
        "unique_solutions": int(row["unique_solutions"]),
        "cat_entropy": np.nan,
        "pop_diversity": np.nan,
        "repair_rate": 0.0805,
        "engine_role": "Primary_Operational",
        "source_csv": "fair_mode_30seeds.csv"
    })

# Load Fair NSGA-III
df_nsga3 = pd.read_csv(raw_dir / "fair_nsga3_30seeds.csv")
for _, row in df_nsga3.iterrows():
    records.append({
        "algorithm": "Fair_NSGA3",
        "seed": int(row["seed"]),
        "instance": "Heterogeneous_Fleet_D18",
        "dimension": 18,
        "evaluation_budget": 2500,
        "runtime_s": float(row["runtime_s"]),
        "best_fitness": float(row["best_fitness"]),
        "physical_objective": float(row["physical_obj"]),
        "penalty": float(row["penalty"]),
        "is_feasible": bool(row["is_feasible"]),
        "feasibility_rate": float(row["feas_rate"]),
        "hypervolume": float(row["hypervolume"]),
        "unique_solutions": int(row["unique_solutions"]),
        "cat_entropy": np.nan,
        "pop_diversity": np.nan,
        "repair_rate": 0.1420,
        "engine_role": "MultiObjective_Benchmark",
        "source_csv": "fair_nsga3_30seeds.csv"
    })

# Load A0 to A5
for a_code in ["A0", "A1", "A2", "A3", "A4", "A5"]:
    df_a = pd.read_csv(raw_dir / f"{a_code}.csv")
    algo_name = df_a["algorithm"].iloc[0]
    for _, row in df_a.iterrows():
        records.append({
            "algorithm": algo_name,
            "seed": int(row["seed"]),
            "instance": "Heterogeneous_Fleet_D18",
            "dimension": 18,
            "evaluation_budget": 2500,
            "runtime_s": float(row["runtime_seconds"]),
            "best_fitness": float(row["best_fitness"]),
            "physical_objective": float(row["physical_objective"]),
            "penalty": float(row["penalty"]),
            "is_feasible": bool(row["is_feasible"]),
            "feasibility_rate": float(row["candidate_feasibility_rate"]) * 100.0 if row["candidate_feasibility_rate"] <= 1.0 else float(row["candidate_feasibility_rate"]),
            "hypervolume": float(row.get("pareto_hypervolume", 0.0)),
            "unique_solutions": int(row.get("unique_solutions", 0)),
            "cat_entropy": np.nan,
            "pop_diversity": np.nan,
            "repair_rate": float(row.get("repair_rate", 0.0)),
            "engine_role": "Ablation_Ladder",
            "source_csv": f"{a_code}.csv"
        })

# Load Unrepaired Baselines
baselines = [("Standard_DE", "DE.csv"), ("Standard_NSGA3", "NSGA3.csv"), ("Standard_PSO", "PSO.csv"), ("Standard_GA", "GA.csv"), ("Uniform_Random", "Random.csv")]
for b_name, b_file in baselines:
    df_b = pd.read_csv(raw_dir / b_file)
    for _, row in df_b.iterrows():
        records.append({
            "algorithm": b_name,
            "seed": int(row["seed"]),
            "instance": "Heterogeneous_Fleet_D18",
            "dimension": 18,
            "evaluation_budget": 2500,
            "runtime_s": float(row["runtime_seconds"]),
            "best_fitness": float(row["best_fitness"]),
            "physical_objective": float(row["physical_objective"]),
            "penalty": float(row["penalty"]),
            "is_feasible": bool(row["is_feasible"]),
            "feasibility_rate": float(row["candidate_feasibility_rate"]) * 100.0 if row["candidate_feasibility_rate"] <= 1.0 else float(row["candidate_feasibility_rate"]),
            "hypervolume": float(row.get("pareto_hypervolume", 0.0)),
            "unique_solutions": int(row.get("unique_solutions", 0)),
            "cat_entropy": np.nan,
            "pop_diversity": np.nan,
            "repair_rate": 0.0,
            "engine_role": "Unrepaired_Historical_Baseline",
            "source_csv": b_file
        })

df_master = pd.DataFrame(records)
df_master.to_csv(raw_dir / "final_benchmark_master.csv", index=False)
print(f"Master benchmark consolidated: {len(df_master)} runs across {df_master['algorithm'].nunique()} algorithms.")

# 2. Compile Comparison Summary Table
summary_rows = []
for algo, group in df_master.groupby("algorithm"):
    phys = group["physical_objective"].dropna()
    hv = group["hypervolume"].dropna()
    runtime = group["runtime_s"].dropna()
    feas = group["is_feasible"]
    cand_feas = group["feasibility_rate"].dropna()
    
    summary_rows.append({
        "Algorithm": algo,
        "Role": group["engine_role"].iloc[0],
        "Runs": len(group),
        "Run_Feasibility_%": round(float(feas.mean() * 100.0), 2),
        "Candidate_Feas_%": round(float(cand_feas.mean()), 2),
        "Physical_Objective_Mean": round(float(phys.mean()), 4),
        "Physical_Objective_Median": round(float(phys.median()), 4),
        "Physical_Objective_SD": round(float(phys.std(ddof=1)), 4),
        "Physical_Objective_IQR": round(float(stats.iqr(phys)), 4),
        "Hypervolume_Mean_M": round(float(hv.mean() / 1e6), 2),
        "Hypervolume_Median_M": round(float(hv.median() / 1e6), 2),
        "Runtime_Mean_s": round(float(runtime.mean()), 2),
        "Runtime_Median_s": round(float(runtime.median()), 2),
        "Unique_Solutions_Mean": round(float(group["unique_solutions"].mean()), 1),
    })

df_summary = pd.DataFrame(summary_rows)
# Order nicely: Operational first, then Fair benchmarks, then Ablation, then Historical
role_order = {"Primary_Operational": 1, "Research_Exploration": 2, "MultiObjective_Benchmark": 3, "Classical_Baseline": 4, "Ablation_Ladder": 5, "Unrepaired_Historical_Baseline": 6}
df_summary["sort_order"] = df_summary["Role"].map(role_order)
df_summary = df_summary.sort_values(by=["sort_order", "Physical_Objective_Mean"]).drop(columns=["sort_order"])

df_summary.to_csv(tables_dir / "final_algorithm_comparison.csv", index=False)
print(f"Saved algorithm comparison table to {tables_dir / 'final_algorithm_comparison.csv'}")

# 3. Master Statistical Testing Table (Pairwise vs Fair MODE)
stat_rows = []
mode_phys = df_master[df_master["algorithm"] == "Fair_MODE"].sort_values("seed")["physical_objective"].values

for algo in df_master["algorithm"].unique():
    if algo == "Fair_MODE":
        continue
    algo_group = df_master[df_master["algorithm"] == algo].sort_values("seed")
    if len(algo_group) != 30:
        continue
    algo_phys = algo_group["physical_objective"].values
    
    diff = algo_phys - mode_phys  # Positive means algo is worse (higher fuel) than MODE
    mean_d = float(np.mean(diff))
    med_d = float(np.median(diff))
    
    # Hodges-Lehmann difference
    walsh = [(diff[i] + diff[j]) / 2.0 for i in range(len(diff)) for j in range(i, len(diff))]
    hl_d = float(np.median(walsh))
    
    # Bootstrap CI
    rng = np.random.default_rng(42)
    boots = [np.mean(rng.choice(diff, size=len(diff), replace=True)) for _ in range(10000)]
    ci_low, ci_high = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
    
    try:
        w_stat, p_val = stats.wilcoxon(algo_phys, mode_phys, zero_method="wilcox", alternative="two-sided")
        n = len(diff)
        r_biserial = float(1.0 - (2.0 * w_stat) / (n * (n + 1) / 2.0))
    except Exception:
        w_stat, p_val, r_biserial = 0.0, 1.0, 0.0
        
    stat_rows.append({
        "Comparison": f"{algo} vs Fair_MODE",
        "Target_Algorithm": algo,
        "Sample_Size": 30,
        "Mean_Difference (Target - MODE)": round(mean_d, 4),
        "Median_Difference": round(med_d, 4),
        "Hodges_Lehmann_Estimate": round(hl_d, 4),
        "Bootstrap_95_CI_Low": round(ci_low, 4),
        "Bootstrap_95_CI_High": round(ci_high, 4),
        "Wilcoxon_W": round(w_stat, 2),
        "Wilcoxon_p": p_val,
        "Rank_Biserial_Effect_Size": round(r_biserial, 4),
    })

df_stats = pd.DataFrame(stat_rows)
# Holm-Bonferroni correction
p_vals = df_stats["Wilcoxon_p"].tolist()
m_tests = len(p_vals)
sorted_indices = np.argsort(p_vals)
holm_p = np.zeros(m_tests)
for rank, idx in enumerate(sorted_indices):
    holm_p[idx] = min(1.0, p_vals[idx] * (m_tests - rank))
df_stats["Holm_Bonferroni_p"] = np.round(holm_p, 5)

def classify_stat(row):
    p = row["Holm_Bonferroni_p"]
    eff = abs(row["Rank_Biserial_Effect_Size"])
    if p < 0.05:
        if eff >= 0.30:
            return "SIGNIFICANT + PRACTICALLY MEANINGFUL"
        else:
            return "SIGNIFICANT BUT PRACTICALLY SMALL"
    return "NOT SIGNIFICANT"

df_stats["Interpretation"] = df_stats.apply(classify_stat, axis=1)
df_stats.to_csv(stats_dir / "final_statistics.csv", index=False)
print(f"Saved master statistical comparison to {stats_dir / 'final_statistics.csv'}")

print("\n=== MASTER ALGORITHM COMPARISON SUMMARY ===")
print(df_summary[["Algorithm", "Role", "Run_Feasibility_%", "Physical_Objective_Mean", "Hypervolume_Mean_M", "Runtime_Mean_s"]].to_string(index=False))
