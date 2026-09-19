import pandas as pd
import numpy as np
from scipy import stats

df_nsga3 = pd.read_csv('results/raw/fair_nsga3_30seeds.csv')
df_mode = pd.read_csv('results/raw/fair_mode_30seeds.csv')
df_a5 = pd.read_csv('PHASE5/results/A5.csv')

print('=== 30-SEED FAIR BENCHMARK SUMMARY ===')
configs = [
    ('Fair NSGA-III', df_nsga3, 'best_fitness', 'physical_obj', 'hypervolume', 'runtime_s'),
    ('Fair MODE', df_mode, 'best_fitness', 'physical_obj', 'hypervolume', 'runtime_s'),
    ('A5 Complete Hybrid QI', df_a5, 'best_fitness', 'physical_objective', 'pareto_hypervolume', 'runtime_seconds')
]

for name, df, col_fit, col_phys, col_hv, col_t in configs:
    feas = float(df['is_feasible'].mean() * 100.0)
    fit_m, fit_med, fit_std = float(df[col_fit].mean()), float(df[col_fit].median()), float(df[col_fit].std())
    phys_m, phys_med, phys_std = float(df[col_phys].mean()), float(df[col_phys].median()), float(df[col_phys].std())
    hv_m, hv_med = float(df[col_hv].mean()), float(df[col_hv].median())
    t_m = float(df[col_t].mean())
    print(f"{name:22} | Feas: {feas:5.1f}% | Fit: {fit_m:7.2f} (med: {fit_med:6.2f}) | Phys: {phys_m:5.2f} (med: {phys_med:5.2f}) | HV: {hv_m/1e6:6.2f}M | Time: {t_m:5.2f}s")

# Paired tests between Fair MODE and Fair A5
print('\n=== PAIRED STATISTICAL TESTS (Fair MODE vs Fair A5) ===')
w_phys = stats.wilcoxon(df_mode['physical_obj'].values, df_a5['physical_objective'].values)
w_hv = stats.wilcoxon(df_mode['hypervolume'].values, df_a5['pareto_hypervolume'].values)
w_time = stats.wilcoxon(df_mode['runtime_s'].values, df_a5['runtime_seconds'].values)

diff_phys = df_mode['physical_obj'].values - df_a5['physical_objective'].values
diff_hv = df_mode['hypervolume'].values - df_a5['pareto_hypervolume'].values

print(f"Physical Obj (MODE vs A5): MODE mean={df_mode['physical_obj'].mean():.4f}, A5 mean={df_a5['physical_objective'].mean():.4f}, diff={diff_phys.mean():.4f}, W={w_phys.statistic}, p={w_phys.pvalue:.6e}")
print(f"Hypervolume (MODE vs A5): MODE mean={df_mode['hypervolume'].mean()/1e6:.2f}M, A5 mean={df_a5['pareto_hypervolume'].mean()/1e6:.2f}M, diff={diff_hv.mean()/1e6:.2f}M, W={w_hv.statistic}, p={w_hv.pvalue:.6e}")
print(f"Runtime (MODE vs A5): MODE mean={df_mode['runtime_s'].mean():.2f}s, A5 mean={df_a5['runtime_seconds'].mean():.2f}s, W={w_time.statistic}, p={w_time.pvalue:.6e}")

# Paired tests between Fair NSGA-III and Fair A5
print('\n=== PAIRED STATISTICAL TESTS (Fair NSGA-III vs Fair A5) ===')
w_phys_n = stats.wilcoxon(df_nsga3['physical_obj'].values, df_a5['physical_objective'].values)
w_hv_n = stats.wilcoxon(df_nsga3['hypervolume'].values, df_a5['pareto_hypervolume'].values)
diff_hv_n = df_nsga3['hypervolume'].values - df_a5['pareto_hypervolume'].values

print(f"Physical Obj (NSGA3 vs A5): NSGA3 mean={df_nsga3['physical_obj'].mean():.4f}, A5 mean={df_a5['physical_objective'].mean():.4f}, W={w_phys_n.statistic}, p={w_phys_n.pvalue:.6e}")
print(f"Hypervolume (NSGA3 vs A5): NSGA3 mean={df_nsga3['hypervolume'].mean()/1e6:.2f}M, A5 mean={df_a5['pareto_hypervolume'].mean()/1e6:.2f}M, diff={diff_hv_n.mean()/1e6:.2f}M, W={w_hv_n.statistic}, p={w_hv_n.pvalue:.6e}")
