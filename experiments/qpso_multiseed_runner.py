"""
Multi-Seed QPSO vs Random Search Benchmark & Statistical Hypothesis Testing.
Phase 2.1 Evidence Hardening (Sections 2, 3, 4).
Runs 30 matched independent seeds under strict equal 225-evaluation budgets.
Generates:
- results/experiments/qpso_random_multiseed.csv
- results/experiments/qpso_random_statistics.json
"""

import json
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import mean_absolute_error

from common.logger import get_logger
from common.reproducibility import get_git_commit
from data.data_quality import DataQualityAuditor
from data.splitting import LeakageSafeSplitter
from prediction.ml_baseline import CONFIG_A_FEATURES
from prediction.physics_predictor import PhysicsFuelPredictor
from prediction.qpso_model_selection import (
    HyperparameterSearchSpace,
    QPSOModelSelector,
    RandomSearchModelSelector,
)
from prediction.residual_model import HybridResidualPredictor

logger = get_logger("qpso_multiseed_runner")


def run_multiseed_benchmark(
    seeds: Optional[List[int]] = None,
    eval_budget: int = 225,
    results_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    if results_dir is None:
        results_dir = Path(__file__).resolve().parent.parent / "results" / "experiments"
    results_dir.mkdir(parents=True, exist_ok=True)

    if seeds is None:
        # Minimum 10 independent seeds per Section 2
        seeds = [42, 101, 202, 303, 404, 505, 606, 707, 808, 909]

    data_path = Path(__file__).resolve().parent.parent / "data" / "synthetic" / "synthetic_vessel_telemetry.csv"
    df_raw = pd.read_csv(data_path)

    # Clean valid records matching exp_phase2_runner protocol
    clean_mask = (
        df_raw["fuel_mass_flow_kg_h"].notna() &
        (df_raw["fuel_mass_flow_kg_h"] > 0) &
        df_raw["shaft_power_kw"].notna() &
        (df_raw["shaft_power_kw"] >= 0) &
        df_raw["stw_kn"].notna() &
        (df_raw["stw_kn"] > 0) &
        df_raw["sog_kn"].notna() &
        (df_raw["sog_kn"] > 0) &
        (df_raw["latitude"] >= -90) & (df_raw["latitude"] <= 90) &
        (df_raw["longitude"] >= -180) & (df_raw["longitude"] <= 180)
    )
    df_clean = df_raw[clean_mask].drop_duplicates().copy()

    splitter = LeakageSafeSplitter(train_ratio=0.70, val_ratio=0.15, test_ratio=0.15)
    train_df, val_df, test_df = splitter.temporal_split(df_clean)

    y_test = test_df["fuel_mass_flow_kg_h"].values

    # Precompute physics once on all partitions
    physics_model = PhysicsFuelPredictor()
    f_phys_train = physics_model.predict(train_df)
    f_phys_val = physics_model.predict(val_df)
    f_phys_test = physics_model.predict(test_df)

    rows = []
    logger.info(f"Starting multi-seed evaluation across {len(seeds)} matched seeds (budget={eval_budget})...")

    qpso_val_maes = []
    qpso_test_maes = []
    qpso_runtimes = []

    rs_val_maes = []
    rs_test_maes = []
    rs_runtimes = []

    for idx, seed in enumerate(seeds, 1):
        logger.info(f"[{idx}/{len(seeds)}] Evaluating seed={seed}...")

        # 1. QPSO Search (15 particles * 15 iterations = 225 evaluations)
        qpso_selector = QPSOModelSelector(n_particles=15, max_iterations=15, seed=seed)
        qpso_res = qpso_selector.search(
            train_df=train_df,
            val_df=val_df,
            feature_cols=CONFIG_A_FEATURES,
            f_phys_train=f_phys_train,
            f_phys_val=f_phys_val,
        )
        qpso_val_mae = float(qpso_res["best_validation_mae"])
        qpso_time = float(qpso_res["wall_clock_runtime_s"])

        # Retrain QPSO model on train with optimal parameters and evaluate on test
        qpso_p = qpso_res["best_params"]
        lgb_qpso_params = {
            "n_estimators": 100,
            "learning_rate": qpso_p["learning_rate"],
            "num_leaves": qpso_p["num_leaves"],
            "max_depth": qpso_p["max_depth"],
            "min_child_samples": qpso_p["min_child_samples"],
            "colsample_bytree": qpso_p["feature_fraction"],
            "reg_alpha": qpso_p["reg_alpha"],
            "reg_lambda": qpso_p["reg_lambda"],
            "random_state": seed,
            "n_jobs": -1,
            "verbose": -1,
        }
        m_qpso = HybridResidualPredictor(
            feature_cols=CONFIG_A_FEATURES,
            hyperparameters=lgb_qpso_params,
            alpha=qpso_p["alpha_residual"],
            seed=seed,
        )
        m_qpso.fit(train_df, target_col="fuel_mass_flow_kg_h", f_phys_train=f_phys_train)
        pred_qpso_test = m_qpso.predict(test_df, f_phys=f_phys_test)
        qpso_test_mae = float(mean_absolute_error(y_test, pred_qpso_test))

        # 2. Random Search (225 evaluations)
        rs_selector = RandomSearchModelSelector(total_budget=eval_budget, seed=seed)
        rs_res = rs_selector.search(
            train_df=train_df,
            val_df=val_df,
            feature_cols=CONFIG_A_FEATURES,
            f_phys_train=f_phys_train,
            f_phys_val=f_phys_val,
        )
        rs_val_mae = float(rs_res["best_validation_mae"])
        rs_time = float(rs_res["wall_clock_runtime_s"])

        rs_p = rs_res["best_params"]
        lgb_rs_params = {
            "n_estimators": 100,
            "learning_rate": rs_p["learning_rate"],
            "num_leaves": rs_p["num_leaves"],
            "max_depth": rs_p["max_depth"],
            "min_child_samples": rs_p["min_child_samples"],
            "colsample_bytree": rs_p["feature_fraction"],
            "reg_alpha": rs_p["reg_alpha"],
            "reg_lambda": rs_p["reg_lambda"],
            "random_state": seed,
            "n_jobs": -1,
            "verbose": -1,
        }
        m_rs = HybridResidualPredictor(
            feature_cols=CONFIG_A_FEATURES,
            hyperparameters=lgb_rs_params,
            alpha=rs_p["alpha_residual"],
            seed=seed,
        )
        m_rs.fit(train_df, target_col="fuel_mass_flow_kg_h", f_phys_train=f_phys_train)
        pred_rs_test = m_rs.predict(test_df, f_phys=f_phys_test)
        rs_test_mae = float(mean_absolute_error(y_test, pred_rs_test))

        rows.append({
            "seed": seed,
            "algorithm": "QPSO",
            "best_validation_MAE": qpso_val_mae,
            "final_test_MAE": qpso_test_mae,
            "runtime_s": qpso_time,
            "objective_evaluations": eval_budget,
        })
        rows.append({
            "seed": seed,
            "algorithm": "RandomSearch",
            "best_validation_MAE": rs_val_mae,
            "final_test_MAE": rs_test_mae,
            "runtime_s": rs_time,
            "objective_evaluations": eval_budget,
        })

        qpso_val_maes.append(qpso_val_mae)
        qpso_test_maes.append(qpso_test_mae)
        qpso_runtimes.append(qpso_time)

        rs_val_maes.append(rs_val_mae)
        rs_test_maes.append(rs_test_mae)
        rs_runtimes.append(rs_time)

    # Export raw multi-seed results
    df_multiseed = pd.DataFrame(rows)
    csv_out = results_dir / "qpso_random_multiseed.csv"
    df_multiseed.to_csv(csv_out, index=False)
    logger.info(f"Saved multi-seed results to {csv_out}")

    # =========================================================================
    # Section 3: Statistical Analysis
    # =========================================================================
    def compute_summary_stats(arr: List[float]) -> Dict[str, float]:
        a = np.array(arr, dtype=float)
        mean_val = float(np.mean(a))
        std_val = float(np.std(a, ddof=1)) if len(a) > 1 else 0.0
        median_val = float(np.median(a))
        n = len(a)
        ci_half = float(stats.t.ppf(0.975, df=n - 1) * (std_val / np.sqrt(n))) if n > 1 and std_val > 0 else 0.0
        return {
            "mean": mean_val,
            "median": median_val,
            "std": std_val,
            "ci_95_low": mean_val - ci_half,
            "ci_95_high": mean_val + ci_half,
        }

    diff_val = np.array(qpso_val_maes) - np.array(rs_val_maes)
    diff_test = np.array(qpso_test_maes) - np.array(rs_test_maes)

    # Wilcoxon signed-rank test
    w_val_stat, w_val_p = stats.wilcoxon(diff_val, alternative="two-sided") if len(diff_val) >= 5 else (0.0, 1.0)
    w_test_stat, w_test_p = stats.wilcoxon(diff_test, alternative="two-sided") if len(diff_test) >= 5 else (0.0, 1.0)

    # Effect sizes (Cohen's d)
    d_val = float(np.mean(diff_val) / np.std(diff_val, ddof=1)) if np.std(diff_val, ddof=1) > 0 else 0.0
    d_test = float(np.mean(diff_test) / np.std(diff_test, ddof=1)) if np.std(diff_test, ddof=1) > 0 else 0.0

    stats_report = {
        "metadata": {
            "num_seeds": len(seeds),
            "evaluation_budget_per_seed": eval_budget,
            "git_commit": get_git_commit(),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
        "qpso": {
            "validation_mae": compute_summary_stats(qpso_val_maes),
            "test_mae": compute_summary_stats(qpso_test_maes),
            "runtime_s": compute_summary_stats(qpso_runtimes),
        },
        "random_search": {
            "validation_mae": compute_summary_stats(rs_val_maes),
            "test_mae": compute_summary_stats(rs_test_maes),
            "runtime_s": compute_summary_stats(rs_runtimes),
        },
        "paired_differences": {
            "validation_mae_diff_qpso_minus_rs": compute_summary_stats(diff_val.tolist()),
            "test_mae_diff_qpso_minus_rs": compute_summary_stats(diff_test.tolist()),
        },
        "hypothesis_tests": {
            "wilcoxon_signed_rank_validation_mae": {
                "statistic": float(w_val_stat),
                "p_value": float(w_val_p),
                "effect_size_cohens_d": d_val,
                "null_hypothesis": "Median paired difference (QPSO - RS) is zero",
                "is_statistically_significant_0_05": bool(w_val_p < 0.05),
            },
            "wilcoxon_signed_rank_test_mae": {
                "statistic": float(w_test_stat),
                "p_value": float(w_test_p),
                "effect_size_cohens_d": d_test,
                "null_hypothesis": "Median paired difference (QPSO - RS) is zero",
                "is_statistically_significant_0_05": bool(w_test_p < 0.05),
            },
        },
    }

    json_out = results_dir / "qpso_random_statistics.json"
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(stats_report, f, indent=2)
    logger.info(f"Saved statistical analysis report to {json_out}")

    return stats_report


if __name__ == "__main__":
    run_multiseed_benchmark()
