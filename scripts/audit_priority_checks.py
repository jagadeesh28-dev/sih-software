import pandas as pd
import numpy as np
from scipy import stats

de_df = pd.read_csv('PHASE5/results/DE.csv')
a5_df = pd.read_csv('PHASE5/results/A5.csv')

print('DE Columns:', de_df.columns.tolist())
print('A5 Columns:', a5_df.columns.tolist())

# Check seeds match
assert (de_df['seed'] == a5_df['seed']).all(), 'Seeds do not match!'
print(f"Matched seeds: {len(de_df)} seeds from {de_df['seed'].min()} to {de_df['seed'].max()}")

metrics = ['best_fitness', 'physical_objective', 'runtime_seconds', 'pareto_hypervolume']
results = {}

for metric in metrics:
    de_vals = de_df[metric].values
    a5_vals = a5_df[metric].values
    diff = a5_vals - de_vals
    
    # Stats for DE
    de_mean, de_med, de_std = float(np.mean(de_vals)), float(np.median(de_vals)), float(np.std(de_vals, ddof=1))
    de_p10, de_p25, de_p75, de_p90 = [float(x) for x in np.percentile(de_vals, [10, 25, 75, 90])]
    de_iqr = de_p75 - de_p25
    
    # Stats for A5
    a5_mean, a5_med, a5_std = float(np.mean(a5_vals)), float(np.median(a5_vals)), float(np.std(a5_vals, ddof=1))
    a5_p10, a5_p25, a5_p75, a5_p90 = [float(x) for x in np.percentile(a5_vals, [10, 25, 75, 90])]
    a5_iqr = a5_p75 - a5_p25
    
    # Paired Wilcoxon
    try:
        w_res = stats.wilcoxon(a5_vals, de_vals)
        w_stat, w_p = float(w_res.statistic), float(w_res.pvalue)
    except Exception as e:
        w_stat, w_p = np.nan, np.nan
        
    # Effect size (rank-biserial)
    nonzero_diff = diff[diff != 0]
    n = len(nonzero_diff)
    if n > 0 and not np.isnan(w_stat):
        total_rank = n * (n + 1) / 2
        r_rb = float((total_rank - 2 * w_stat) / total_rank)
    else:
        r_rb = 0.0
        
    # Bootstrap 95% CI on mean difference
    rng = np.random.default_rng(42)
    boot_diffs = [np.mean(rng.choice(diff, size=len(diff), replace=True)) for _ in range(10000)]
    ci_low, ci_high = [float(x) for x in np.percentile(boot_diffs, [2.5, 97.5])]
    
    print(f"=== Metric: {metric} ===")
    print(f"DE: Mean={de_mean:.4f}, Med={de_med:.4f}, SD={de_std:.4f}, IQR={de_iqr:.4f}, P10={de_p10:.4f}, P90={de_p90:.4f}")
    print(f"A5: Mean={a5_mean:.4f}, Med={a5_med:.4f}, SD={a5_std:.4f}, IQR={a5_iqr:.4f}, P10={a5_p10:.4f}, P90={a5_p90:.4f}")
    print(f"Mean Diff (A5 - DE): {np.mean(diff):.4f}, 95% CI: [{ci_low:.4f}, {ci_high:.4f}]")
    print(f"Wilcoxon W: {w_stat}, p-value: {w_p:.6e}, Effect Size (r_rb): {r_rb:.4f}")
    print()
    results[metric] = {
        "de": {"mean": de_mean, "median": de_med, "std": de_std, "iqr": de_iqr, "p10": de_p10, "p90": de_p90},
        "a5": {"mean": a5_mean, "median": a5_med, "std": a5_std, "iqr": a5_iqr, "p10": a5_p10, "p90": a5_p90},
        "mean_diff": float(np.mean(diff)),
        "ci": [ci_low, ci_high],
        "w_stat": w_stat,
        "w_p": w_p,
        "r_rb": r_rb
    }
