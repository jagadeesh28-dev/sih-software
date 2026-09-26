import os
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

base_dir = str(Path(__file__).resolve().parents[1] / "PHASE5")
val_dir = os.path.join(base_dir, "validation")

print("=== RUNTIME POWER-LAW FIT T(D) = a * D^b ===")
sc_df = pd.read_csv(os.path.join(val_dir, "scalability.csv"))
a5_sc = sc_df[sc_df["optimizer"] == "A5_Complete_Hybrid_QI"]
de_sc = sc_df[sc_df["optimizer"] == "DE"]

log_d = np.log(a5_sc["dimension"].values)
log_t_a5 = np.log(a5_sc["mean_runtime_seconds"].values)
res_a5 = stats.linregress(log_d, log_t_a5)
print(f"A5 Scaling: b = {res_a5.slope:.4f} (SE={res_a5.stderr:.4f}), R^2 = {res_a5.rvalue**2:.4f}, a = {np.exp(res_a5.intercept):.6f}")

log_t_de = np.log(de_sc["mean_runtime_seconds"].values)
res_de = stats.linregress(log_d, log_t_de)
print(f"DE Scaling: b = {res_de.slope:.4f} (SE={res_de.stderr:.4f}), R^2 = {res_de.rvalue**2:.4f}, a = {np.exp(res_de.intercept):.6f}")

# Check Friedman Omnibus test across 11 algorithms
res_dir = os.path.join(base_dir, "results")
algos = ["A0", "A1", "A2", "A3", "A4", "A5", "DE", "PSO", "GA", "Random", "NSGA3"]
dfs = [pd.read_csv(os.path.join(res_dir, f"{a}.csv"))["best_fitness"].values for a in algos]
fried_stat, fried_p = stats.friedmanchisquare(*dfs)
print(f"\n=== FRIEDMAN OMNIBUS TEST ===")
print(f"Chi-square = {fried_stat:.4f}, p-value = {fried_p:.5e}")

# Check physical fitness Friedman test for feasible algorithms: A1, A2, A4, A5, DE
dfs_phys = [pd.read_csv(os.path.join(res_dir, f"{a}.csv"))["physical_objective"].values for a in ["A1", "A2", "A4", "A5", "DE"]]
fried_phys_stat, fried_phys_p = stats.friedmanchisquare(*dfs_phys)
print(f"Physical Fitness (Feasible algos A1, A2, A4, A5, DE): Chi-square = {fried_phys_stat:.4f}, p-value = {fried_phys_p:.5e}")

# Check small_exact.csv
print("\n=== SMALL EXACT CSV CONTENT ===")
exact_df = pd.read_csv(os.path.join(val_dir, "small_exact.csv"))
print(exact_df.to_string(index=False))
