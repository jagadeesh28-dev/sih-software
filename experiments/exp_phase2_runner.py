"""
Phase 2 Experiment Runner.
Executes:
- EXP-PRED-01: Physics-Only Baseline
- EXP-PRED-02: ML-Only Baseline (CONFIG-A)
- EXP-PRED-03: Physics + ML Residual (with discrete alpha sweep in {0.0, 0.25, 0.50, 0.75, 1.00})
- EXP-PRED-04: Physics + ML Residual + QPSO vs. Random Search (equal budget)
- EXP-PRED-05: Temporal Generalization Analysis
- EXP-PRED-06: Leave-Vessel-Out Cross-Vessel Generalization (strictly using CONFIG-A)
- EXP-PRED-07: Systematic Ablation Study (Information sources, environmental channels, and vessel_id)
Also executes:
- Quantile Uncertainty Evaluation (pinball loss q05, q50, q95, non-crossing)
- Sliced Diagnostic Error Analysis across speed, draft, wave, wind, and engine load.
Outputs:
- results/experiments/prediction_comparison.csv
- results/experiments/cross_vessel_results.csv
- results/experiments/ablation_study.csv
- results/experiments/error_analysis/
- results/experiments/<exp_id>/
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Ensure repository root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import yaml

from common.logger import setup_logger
from common.reproducibility import audit_environment, get_git_commit, set_seed
from data.splitting import LeakageSafeSplitter
from prediction.physics_predictor import PhysicsFuelPredictor
from prediction.ml_baseline import PureMLPredictor, CONFIG_A_FEATURES, CONFIG_B_FEATURES
from prediction.residual_model import HybridResidualPredictor
from prediction.qpso_model_selection import QPSOModelSelector, RandomSearchModelSelector
from prediction.quantile_model import QuantileUncertaintyPredictor
from prediction.error_analysis import DiagnosticErrorAnalyzer
from prediction.evaluate import evaluate_predictions, evaluate_quantiles

logger = setup_logger("exp_phase2_runner")


def save_experiment_folder(
    output_dir: Path,
    exp_id: str,
    config: Dict[str, Any],
    metrics: Dict[str, Any],
    y_true: np.ndarray,
    y_pred: np.ndarray,
    df_test: pd.DataFrame,
    description: str,
):
    folder = output_dir / exp_id
    folder.mkdir(parents=True, exist_ok=True)
    plots_dir = folder / "plots"
    plots_dir.mkdir(exist_ok=True)

    # 1. config.yaml
    env_info = audit_environment()
    full_config = {
        "experiment_id": exp_id,
        "description": description,
        "dataset_id": "DS-SYNTH-2026-01",
        "dataset_type": "SYNTHETIC_TEST_DATA",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": get_git_commit(),
        "environment": env_info,
        "model_config": config,
    }
    with open(folder / "config.yaml", "w", encoding="utf-8") as f:
        yaml.dump(full_config, f, default_flow_style=False, sort_keys=False)

    # 2. metrics.json
    with open(folder / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    # 3. predictions.csv
    pred_df = pd.DataFrame({
        "timestamp": df_test["timestamp"].values if "timestamp" in df_test.columns else np.arange(len(y_true)),
        "vessel_id": df_test["vessel_id"].values if "vessel_id" in df_test.columns else "UNKNOWN",
        "fuel_observed_kg_h": y_true,
        "fuel_predicted_kg_h": y_pred,
    })
    pred_df.to_csv(folder / "predictions.csv", index=False)

    # 4. residuals.csv
    res_df = pd.DataFrame({
        "timestamp": pred_df["timestamp"],
        "residual_kg_h": y_true - y_pred,
        "absolute_error_kg_h": np.abs(y_true - y_pred),
        "percentage_error_pct": np.abs((y_true - y_pred) / np.maximum(y_true, 1e-6)) * 100.0,
    })
    res_df.to_csv(folder / "residuals.csv", index=False)

    # 5. README.md
    with open(folder / "README.md", "w", encoding="utf-8") as f:
        f.write(f"# Experiment {exp_id} Artifacts\n\n")
        f.write(f"- **Description**: {description}\n")
        f.write(f"- **Dataset Type**: SYNTHETIC_TEST_DATA\n")
        f.write(f"- **Timestamp UTC**: {datetime.now(timezone.utc).isoformat()}\n")
        f.write(f"- **MAE**: {metrics.get('mae', 'N/A')} kg/h\n")
        f.write(f"- **RMSE**: {metrics.get('rmse', 'N/A')} kg/h\n")
        f.write(f"- **R²**: {metrics.get('r2', 'N/A')}\n")
        f.write(f"- **Test Observations**: {len(y_true)}\n\n")


def run_phase2_experiments():
    set_seed(42)
    pkg_root = Path(__file__).resolve().parent.parent
    data_path = pkg_root / "data" / "synthetic" / "synthetic_vessel_telemetry.csv"
    results_dir = pkg_root / "results" / "experiments"
    results_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Loading dataset for Phase 2 experiments...")
    df_raw = pd.read_csv(data_path)

    # Clean valid records
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
    logger.info(f"Clean modeling dataset: {len(df_clean)} records across {df_clean['vessel_id'].nunique()} vessels.")

    splitter = LeakageSafeSplitter(train_ratio=0.70, val_ratio=0.15, test_ratio=0.15)
    train_df, val_df, test_df = splitter.temporal_split(df_clean)
    y_test = test_df["fuel_mass_flow_kg_h"].values

    logger.info(f"Temporal Split sizes: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")

    comparison_records = []
    git_hash = get_git_commit()
    now_ts = datetime.now(timezone.utc).isoformat()

    # =========================================================================
    # EXP-PRED-01: Physics-Only Baseline
    # =========================================================================
    logger.info("Running EXP-PRED-01: Physics-Only Baseline (STW pipeline)...")
    physics_model = PhysicsFuelPredictor()
    pred_phys = physics_model.predict(test_df)
    metrics_phys = evaluate_predictions(y_test, pred_phys)

    rec_phys = {
        "experiment_id": "EXP-PRED-01",
        "model": "Physics-Only",
        "split_type": "chronological_70_15_15",
        "vessel_scope": "all_vessels",
        "dataset_id": "DS-SYNTH-2026-01",
        "dataset_type": "SYNTHETIC_TEST_DATA",
        "MAE": metrics_phys["mae"],
        "RMSE": metrics_phys["rmse"],
        "MAPE": metrics_phys["mape_pct"],
        "R2": metrics_phys["r2"],
        "mean_error": metrics_phys["mean_error"],
        "median_absolute_error": metrics_phys["median_absolute_error"],
        "max_absolute_error": metrics_phys["max_absolute_error"],
        "training_rows": 0,
        "validation_rows": 0,
        "test_rows": len(test_df),
        "seed": 42,
        "git_hash": git_hash,
        "timestamp": now_ts,
    }
    comparison_records.append(rec_phys)

    save_experiment_folder(
        output_dir=results_dir,
        exp_id="EXP-PRED-01",
        config={"model_type": "Physics-Only (Hydrodynamic Resistance & Propulsion via STW)"},
        metrics=metrics_phys,
        y_true=y_test,
        y_pred=pred_phys,
        df_test=test_df,
        description="First-principles naval architecture model using STW, ITTC-1957 friction, and Holtrop-Mennen.",
    )

    # =========================================================================
    # EXP-PRED-02: ML-Only Baseline (CONFIG-A)
    # =========================================================================
    logger.info("Running EXP-PRED-02: ML-Only Baseline (CONFIG-A, LightGBM, raw features)...")
    ml_model = PureMLPredictor(feature_cols=CONFIG_A_FEATURES, seed=42)
    ml_model.fit(train_df=train_df, val_df=val_df)
    pred_ml = ml_model.predict(test_df)
    metrics_ml = evaluate_predictions(y_test, pred_ml)

    rec_ml = {
        "experiment_id": "EXP-PRED-02",
        "model": "ML-Only (LightGBM)",
        "split_type": "chronological_70_15_15",
        "vessel_scope": "all_vessels",
        "dataset_id": "DS-SYNTH-2026-01",
        "dataset_type": "SYNTHETIC_TEST_DATA",
        "MAE": metrics_ml["mae"],
        "RMSE": metrics_ml["rmse"],
        "MAPE": metrics_ml["mape_pct"],
        "R2": metrics_ml["r2"],
        "mean_error": metrics_ml["mean_error"],
        "median_absolute_error": metrics_ml["median_absolute_error"],
        "max_absolute_error": metrics_ml["max_absolute_error"],
        "training_rows": len(train_df),
        "validation_rows": len(val_df),
        "test_rows": len(test_df),
        "seed": 42,
        "git_hash": git_hash,
        "timestamp": now_ts,
    }
    comparison_records.append(rec_ml)

    save_experiment_folder(
        output_dir=results_dir,
        exp_id="EXP-PRED-02",
        config=ml_model.training_metadata,
        metrics=metrics_ml,
        y_true=y_test,
        y_pred=pred_ml,
        df_test=test_df,
        description="Pure ML LightGBM baseline trained strictly on TRAIN with early stopping on VALIDATION (CONFIG-A).",
    )

    # =========================================================================
    # EXP-PRED-03: Physics + ML Residual (with alpha sweep)
    # =========================================================================
    logger.info("Running EXP-PRED-03: Physics + ML Residual with Section 9 alpha sweep...")
    hybrid_model = HybridResidualPredictor(
        physics_predictor=physics_model,
        feature_cols=CONFIG_A_FEATURES,
        seed=42,
    )
    hybrid_model.fit(
        train_df=train_df,
        val_df=val_df,
        tune_alpha=True,
        candidate_alphas=[0.0, 0.25, 0.50, 0.75, 1.00],
    )
    pred_hybrid = hybrid_model.predict(test_df)
    metrics_hybrid = evaluate_predictions(y_test, pred_hybrid)

    rec_hybrid = {
        "experiment_id": "EXP-PRED-03",
        "model": f"Physics+ML Residual (alpha={hybrid_model.alpha:.2f})",
        "split_type": "chronological_70_15_15",
        "vessel_scope": "all_vessels",
        "dataset_id": "DS-SYNTH-2026-01",
        "dataset_type": "SYNTHETIC_TEST_DATA",
        "MAE": metrics_hybrid["mae"],
        "RMSE": metrics_hybrid["rmse"],
        "MAPE": metrics_hybrid["mape_pct"],
        "R2": metrics_hybrid["r2"],
        "mean_error": metrics_hybrid["mean_error"],
        "median_absolute_error": metrics_hybrid["median_absolute_error"],
        "max_absolute_error": metrics_hybrid["max_absolute_error"],
        "training_rows": len(train_df),
        "validation_rows": len(val_df),
        "test_rows": len(test_df),
        "seed": 42,
        "git_hash": git_hash,
        "timestamp": now_ts,
    }
    comparison_records.append(rec_hybrid)

    save_experiment_folder(
        output_dir=results_dir,
        exp_id="EXP-PRED-03",
        config=hybrid_model.training_metadata,
        metrics=metrics_hybrid,
        y_true=y_test,
        y_pred=pred_hybrid,
        df_test=test_df,
        description="Hybrid Physics-guided ML residual regressor with validation-tuned alpha weighting.",
    )

    # =========================================================================
    # EXP-PRED-04: QPSO vs. Random Search Model Selection (Equal Budget)
    # =========================================================================
    logger.info("Running EXP-PRED-04: QPSO vs. Random Search Model Selection (225 evaluations each)...")
    qpso_selector = QPSOModelSelector(n_particles=15, max_iterations=15, seed=42)  # 225 evals
    qpso_res = qpso_selector.search(train_df=train_df, val_df=val_df, feature_cols=CONFIG_A_FEATURES)

    random_selector = RandomSearchModelSelector(total_budget=225, seed=42)
    random_res = random_selector.search(train_df=train_df, val_df=val_df, feature_cols=CONFIG_A_FEATURES)

    logger.info(f"QPSO Best Val MAE: {qpso_res['best_validation_mae']:.4f} kg/h (Runtime: {qpso_res['wall_clock_runtime_s']}s)")
    logger.info(f"Random Search Best Val MAE: {random_res['best_validation_mae']:.4f} kg/h (Runtime: {random_res['wall_clock_runtime_s']}s)")

    qpso_p = qpso_res["best_params"]
    qpso_lgb_params = {
        "n_estimators": 100,
        "learning_rate": qpso_p["learning_rate"],
        "num_leaves": qpso_p["num_leaves"],
        "max_depth": qpso_p["max_depth"],
        "min_child_samples": qpso_p["min_child_samples"],
        "colsample_bytree": qpso_p["feature_fraction"],
        "reg_alpha": qpso_p["reg_alpha"],
        "reg_lambda": qpso_p["reg_lambda"],
        "random_state": 42,
        "n_jobs": -1,
        "verbose": -1,
    }
    qpso_tuned_model = HybridResidualPredictor(
        physics_predictor=physics_model,
        feature_cols=CONFIG_A_FEATURES,
        hyperparameters=qpso_lgb_params,
        alpha=qpso_p["alpha_residual"],
        seed=42,
    )
    qpso_tuned_model.fit(train_df=train_df, val_df=val_df)
    pred_qpso = qpso_tuned_model.predict(test_df)
    metrics_qpso = evaluate_predictions(y_test, pred_qpso)

    rec_qpso = {
        "experiment_id": "EXP-PRED-04",
        "model": "Physics+ML (QPSO Tuned)",
        "split_type": "chronological_70_15_15",
        "vessel_scope": "all_vessels",
        "dataset_id": "DS-SYNTH-2026-01",
        "dataset_type": "SYNTHETIC_TEST_DATA",
        "MAE": metrics_qpso["mae"],
        "RMSE": metrics_qpso["rmse"],
        "MAPE": metrics_qpso["mape_pct"],
        "R2": metrics_qpso["r2"],
        "mean_error": metrics_qpso["mean_error"],
        "median_absolute_error": metrics_qpso["median_absolute_error"],
        "max_absolute_error": metrics_qpso["max_absolute_error"],
        "training_rows": len(train_df),
        "validation_rows": len(val_df),
        "test_rows": len(test_df),
        "seed": 42,
        "git_hash": git_hash,
        "timestamp": now_ts,
    }
    comparison_records.append(rec_qpso)

    save_experiment_folder(
        output_dir=results_dir,
        exp_id="EXP-PRED-04",
        config={
            "qpso_search": qpso_res,
            "random_search_comparison": random_res,
            "selected_parameters": qpso_p,
        },
        metrics=metrics_qpso,
        y_true=y_test,
        y_pred=pred_qpso,
        df_test=test_df,
        description="Hybrid residual model tuned via offline QPSO metaheuristic compared against Random Search under equal 225-eval budget.",
    )

    # =========================================================================
    # EXP-PRED-05: Temporal Generalization Analysis
    # =========================================================================
    logger.info("Running EXP-PRED-05: Temporal Generalization Analysis...")
    test_len = len(test_df)
    t_half = test_len // 2
    test_early = test_df.iloc[:t_half]
    test_late = test_df.iloc[t_half:]

    m_early = evaluate_predictions(test_early["fuel_mass_flow_kg_h"].values, qpso_tuned_model.predict(test_early))
    m_late = evaluate_predictions(test_late["fuel_mass_flow_kg_h"].values, qpso_tuned_model.predict(test_late))

    save_experiment_folder(
        output_dir=results_dir,
        exp_id="EXP-PRED-05",
        config={"split": "early_test_vs_late_test", "early_rows": len(test_early), "late_rows": len(test_late)},
        metrics={"early_test_mae": m_early["mae"], "late_test_mae": m_late["mae"], "overall_test_mae": metrics_qpso["mae"]},
        y_true=y_test,
        y_pred=pred_qpso,
        df_test=test_df,
        description="Temporal drift and forward horizon evaluation without lookahead leakage.",
    )

    # =========================================================================
    # EXP-PRED-06: Leave-Vessel-Out Generalization (CONFIG-A Strictly Enforced)
    # =========================================================================
    logger.info("Running EXP-PRED-06: Leave-Vessel-Out Generalization (CONFIG-A, no vessel_id)...")
    vessels = list(df_clean["vessel_id"].unique())
    cross_vessel_rows = []

    for holdout_vessel in vessels:
        train_lvo, test_lvo = splitter.leave_vessel_out_split(df_clean, holdout_vessel_id=holdout_vessel)
        n_lvo = len(train_lvo)
        t_cut = int(n_lvo * 0.80)
        tr_sub = train_lvo.iloc[:t_cut]
        val_sub = train_lvo.iloc[t_cut:]
        y_test_lvo = test_lvo["fuel_mass_flow_kg_h"].values

        # 1. Physics on holdout vessel
        pred_phys_lvo = physics_model.predict(test_lvo)
        m_phys_lvo = evaluate_predictions(y_test_lvo, pred_phys_lvo)

        # 2. Pure ML on holdout vessel (CONFIG-A: strictly NO vessel_id)
        ml_lvo = PureMLPredictor(feature_cols=CONFIG_A_FEATURES, seed=42)
        ml_lvo.fit(train_df=tr_sub, val_df=val_sub)
        pred_ml_lvo = ml_lvo.predict(test_lvo)
        m_ml_lvo = evaluate_predictions(y_test_lvo, pred_ml_lvo)

        # 3. Hybrid on holdout vessel (CONFIG-A)
        hyb_lvo = HybridResidualPredictor(physics_predictor=physics_model, feature_cols=CONFIG_A_FEATURES, seed=42)
        hyb_lvo.fit(train_df=tr_sub, val_df=val_sub, tune_alpha=True, candidate_alphas=[0.0, 0.25, 0.50, 0.75, 1.00])
        pred_hyb_lvo = hyb_lvo.predict(test_lvo)
        m_hyb_lvo = evaluate_predictions(y_test_lvo, pred_hyb_lvo)

        best_m = "ML" if m_ml_lvo["mae"] <= m_hyb_lvo["mae"] else "Hybrid"
        v_type = str(test_lvo["vessel_type"].iloc[0])
        cross_vessel_rows.append({
            "holdout_vessel": holdout_vessel,
            "vessel_type": v_type,
            "feature_config": "CONFIG-A (No vessel_id)",
            "train_vessels": str([v for v in vessels if v != holdout_vessel]),
            "train_samples": len(train_lvo),
            "test_samples": len(test_lvo),
            "physics_mae": m_phys_lvo["mae"],
            "ml_mae": m_ml_lvo["mae"],
            "hybrid_mae": m_hyb_lvo["mae"],
            "hybrid_r2": m_hyb_lvo["r2"],
            "physics_r2": m_phys_lvo["r2"],
            "ml_r2": m_ml_lvo["r2"],
            "best_model": best_m,
        })

    cross_vessel_df = pd.DataFrame(cross_vessel_rows)
    cross_vessel_df.to_csv(results_dir / "cross_vessel_results.csv", index=False)

    save_experiment_folder(
        output_dir=results_dir,
        exp_id="EXP-PRED-06",
        config={"holdout_folds": cross_vessel_rows, "feature_config": "CONFIG-A (Excludes vessel_id)"},
        metrics={
            "mean_holdout_ml_mae": float(cross_vessel_df["ml_mae"].mean()),
            "mean_holdout_hybrid_mae": float(cross_vessel_df["hybrid_mae"].mean()),
            "mean_holdout_physics_mae": float(cross_vessel_df["physics_mae"].mean()),
        },
        y_true=y_test,
        y_pred=pred_qpso,
        df_test=test_df,
        description="Leave-vessel-out evaluation across all 3 vessels using CONFIG-A to prevent identity memorization.",
    )

    # =========================================================================
    # EXP-PRED-07: Ablation Study (Section 16)
    # =========================================================================
    logger.info("Running EXP-PRED-07: Systematic Ablation Study...")
    ablation_records = []

    # Model Family Ablation
    # A. ML-Only
    ablation_records.append({"ablation_category": "Model Family", "variant": "A. ML-Only (CONFIG-A)", "test_mae": metrics_ml["mae"], "test_rmse": metrics_ml["rmse"], "test_r2": metrics_ml["r2"]})
    # B. ML-Only with Engine/Operational Only (No Metocean Environment)
    env_cols = ["wind_speed_ms", "wind_direction_deg", "wave_height_m", "wave_period_s", "wave_direction_deg", "current_speed_ms", "current_direction_deg"]
    no_env_features = [c for c in CONFIG_A_FEATURES if c not in env_cols]
    ml_no_env = PureMLPredictor(feature_cols=no_env_features, seed=42).fit(train_df, val_df)
    m_no_env = evaluate_predictions(y_test, ml_no_env.predict(test_df))
    ablation_records.append({"ablation_category": "Model Family", "variant": "B. ML-Only (No Metocean Environment)", "test_mae": m_no_env["mae"], "test_rmse": m_no_env["rmse"], "test_r2": m_no_env["r2"]})
    # C. Physics + ML Residual
    ablation_records.append({"ablation_category": "Model Family", "variant": "C. Physics + ML Residual (alpha tuned)", "test_mae": metrics_hybrid["mae"], "test_rmse": metrics_hybrid["rmse"], "test_r2": metrics_hybrid["r2"]})
    # D. Physics + ML Residual + QPSO
    ablation_records.append({"ablation_category": "Model Family", "variant": "D. Physics + ML Residual + QPSO", "test_mae": metrics_qpso["mae"], "test_rmse": metrics_qpso["rmse"], "test_r2": metrics_qpso["r2"]})

    # Environmental Channel Ablations (removing one group at a time from CONFIG-A)
    feature_ablations = {
        "Without Wind": ["wind_speed_ms", "wind_direction_deg"],
        "Without Waves": ["wave_height_m", "wave_period_s", "wave_direction_deg"],
        "Without Current": ["current_speed_ms", "current_direction_deg"],
        "Without Draft/Displacement": ["draft_m", "displacement_t"],
        "Without RPM": ["rpm"],
        "Without Shaft Power": ["shaft_power_kw", "shaft_torque_nm"],
    }
    for ab_name, drop_cols in feature_ablations.items():
        sub_feats = [c for c in CONFIG_A_FEATURES if c not in drop_cols]
        m_abl = PureMLPredictor(feature_cols=sub_feats, seed=42).fit(train_df, val_df)
        res_abl = evaluate_predictions(y_test, m_abl.predict(test_df))
        ablation_records.append({
            "ablation_category": "Feature Ablation",
            "variant": ab_name,
            "test_mae": res_abl["mae"],
            "test_rmse": res_abl["rmse"],
            "test_r2": res_abl["r2"],
        })

    # Vessel ID Memorization Ablation (CONFIG-A vs CONFIG-B)
    ml_config_b = PureMLPredictor(feature_cols=CONFIG_B_FEATURES, seed=42).fit(train_df, val_df)
    res_b = evaluate_predictions(y_test, ml_config_b.predict(test_df))
    ablation_records.append({
        "ablation_category": "Vessel ID Memorization",
        "variant": "CONFIG-B (Including vessel_id)",
        "test_mae": res_b["mae"],
        "test_rmse": res_b["rmse"],
        "test_r2": res_b["r2"],
    })

    ablation_df = pd.DataFrame(ablation_records)
    ablation_df.to_csv(results_dir / "ablation_study.csv", index=False)

    save_experiment_folder(
        output_dir=results_dir,
        exp_id="EXP-PRED-07",
        config={"ablation_table": ablation_records},
        metrics={
            "ml_only_mae": metrics_ml["mae"],
            "ml_no_env_mae": m_no_env["mae"],
            "hybrid_mae": metrics_hybrid["mae"],
            "hybrid_qpso_mae": metrics_qpso["mae"],
            "config_b_vessel_id_mae": res_b["mae"],
        },
        y_true=y_test,
        y_pred=pred_ml,
        df_test=test_df,
        description="Ablation study evaluating model architectures, environmental feature contributions, and vessel ID memorization.",
    )

    # =========================================================================
    # Quantile Uncertainty Model (Section 14)
    # =========================================================================
    logger.info("Training Quantile Uncertainty Model (q05, q50, q95, non-crossing)...")
    quantile_model = QuantileUncertaintyPredictor(feature_cols=CONFIG_A_FEATURES, seed=42)
    quantile_model.fit(train_df=train_df, val_df=val_df)
    unc_metrics = quantile_model.evaluate(test_df)
    logger.info(f"Uncertainty Coverage: PICP={unc_metrics['picp_pct']:.2f}% (Nominal: 90%), MPIW={unc_metrics['mpiw']:.2f} kg/h")

    with open(results_dir / "uncertainty_metrics.json", "w", encoding="utf-8") as f:
        json.dump(unc_metrics, f, indent=2)

    # =========================================================================
    # Sliced Diagnostic Error Analysis (Section 17)
    # =========================================================================
    logger.info("Performing Sliced Diagnostic Error Analysis...")
    df_eval = test_df.copy()
    df_eval["y_true"] = y_test
    df_eval["y_phys"] = pred_phys
    df_eval["y_ml"] = pred_ml
    df_eval["y_hybrid"] = pred_hybrid
    DiagnosticErrorAnalyzer.generate_full_error_report(
        df=df_eval,
        y_true_col="y_true",
        y_phys_col="y_phys",
        y_ml_col="y_ml",
        y_hybrid_col="y_hybrid",
        output_dir=results_dir / "error_analysis",
    )

    # Save Unified Comparison Table
    comp_df = pd.DataFrame(comparison_records)
    comp_df.to_csv(results_dir / "prediction_comparison.csv", index=False)
    logger.info(f"Saved prediction comparison table to {results_dir / 'prediction_comparison.csv'}")

    print("\n=== PHASE 2 EXPERIMENTS COMPLETE ===")
    print(comp_df[["experiment_id", "model", "MAE", "RMSE", "R2"]])
    print("\n=== ABLATION STUDY RESULTS ===")
    print(ablation_df[["ablation_category", "variant", "test_mae", "test_r2"]])


if __name__ == "__main__":
    run_phase2_experiments()
