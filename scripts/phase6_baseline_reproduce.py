"""
Phase 6 Baseline Reproduction Script: FuelCast Real Telemetry.
Verifies and reproduces the exact baseline performance of MODEL-REAL-04 (Hybrid Residual):
Target: fuel_mass_flow_kg_h
Vessels: CPS_Poseidon, CPS_Triton, OSS_Ceto (173,986 records total)
Split: Strict Chronological (60% Train, 20% Val, 20% Test per vessel, pooled into fleet partitions)
Features: CONFIG_REAL_A (14 hydrodynamic & metocean features, no machinery power/RPM)
Physics Model: Holtrop-Mennen calm water + wave added resistance + wind resistance
Residual Model: LightGBM Regressor on residual r = y - y_physics
Alpha: 1.0
Expected: R2 = 0.9501, MAE = 246.97 kg/h, MAPE = 14.63%
"""

import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from prediction.evaluate import evaluate_predictions
from prediction.physics_predictor import PhysicsFuelPredictor
from prediction.residual_model import HybridResidualPredictor

PROCESSED_DIR = REPO_ROOT / "data" / "processed" / "real" / "fuelcast"

CONFIG_REAL_A = [
    "stw_kn",
    "sog_kn",
    "draft_m",
    "displacement_t",
    "wind_speed_ms",
    "wind_direction_deg",
    "wave_height_m",
    "wave_period_s",
    "wave_direction_deg",
    "current_speed_ms",
    "current_direction_deg",
    "water_depth_m",
    "vessel_type",
    "fuel_type",
]


def load_and_split():
    vessels = ["CPS_Poseidon", "CPS_Triton", "OSS_Ceto"]
    train_dfs, val_dfs, test_dfs = [], [], []
    vessel_counts = {}

    for v in vessels:
        fpath = PROCESSED_DIR / f"{v}.parquet"
        if not fpath.exists():
            raise FileNotFoundError(f"Missing parquet file: {fpath}")
        df = pd.read_parquet(fpath)
        vessel_counts[v] = len(df)

        n = len(df)
        n_train = int(n * 0.6)
        n_val = int(n * 0.2)
        train_dfs.append(df.iloc[:n_train].copy())
        val_dfs.append(df.iloc[n_train:n_train + n_val].copy())
        test_dfs.append(df.iloc[n_train + n_val:].copy())

    fleet_train = pd.concat(train_dfs, ignore_index=True)
    fleet_val = pd.concat(val_dfs, ignore_index=True)
    fleet_test = pd.concat(test_dfs, ignore_index=True)

    return fleet_train, fleet_val, fleet_test, vessel_counts


def run_baseline_reproduction():
    print("=" * 70)
    print("PHASE 6: BASELINE REPRODUCTION & FORENSIC AUDIT")
    print("=" * 70)

    fleet_train, fleet_val, fleet_test, vessel_counts = load_and_split()
    total_rows = sum(vessel_counts.values())

    print(f"Total Telemetry Records: {total_rows}")
    for v, c in vessel_counts.items():
        print(f"  - {v}: {c:,} rows")
    print(f"Fleet Train Split: {len(fleet_train):,} rows (60.0%)")
    print(f"Fleet Val Split:   {len(fleet_val):,} rows (20.0%)")
    print(f"Fleet Test Split:  {len(fleet_test):,} rows (20.0%)")
    print("-" * 70)

    # 1. Physics-Only (MODEL-REAL-01)
    print("Evaluating MODEL-REAL-01 (Physics Only)...")
    physics = PhysicsFuelPredictor()
    y_phys_test = physics.predict(fleet_test)
    y_true_test = fleet_test["fuel_mass_flow_kg_h"].values
    m_phys = evaluate_predictions(y_true_test, y_phys_test)
    print(f"  Physics MAE:       {m_phys['mae']:.2f} kg/h")
    print(f"  Physics RMSE:      {m_phys['rmse']:.2f} kg/h")
    print(f"  Physics MAPE:      {m_phys['mape_pct']:.2f}%")
    print(f"  Physics R2:        {m_phys['r2']:.4f}")

    # 2. Hybrid Physics + ML Residual (MODEL-REAL-04)
    print("\nTraining MODEL-REAL-04 (Hybrid Residual, alpha=1.0)...")
    hybrid = HybridResidualPredictor(feature_cols=CONFIG_REAL_A, seed=42)
    t0 = time.time()
    hybrid.fit(fleet_train, val_df=fleet_val, tune_alpha=True)
    train_time = time.time() - t0

    y_pred_test = hybrid.predict(fleet_test)
    m_hyb = evaluate_predictions(y_true_test, y_pred_test)

    r2 = float(m_hyb["r2"])
    mae = float(m_hyb["mae"])
    rmse = float(m_hyb["rmse"])
    mape = float(m_hyb["mape_pct"])
    median_ae = float(m_hyb["median_absolute_error"])
    bias = float(m_hyb["mean_error"])

    print(f"  Trained in {train_time:.2f} seconds")
    print(f"  Selected Alpha:    {hybrid.alpha:.2f}")
    print(f"  Reproduced MAE:    {mae:.2f} kg/h  (Target: 246.97)")
    print(f"  Reproduced RMSE:   {rmse:.2f} kg/h  (Target: 443.21)")
    print(f"  Reproduced MAPE:   {mape:.2f}%   (Target: 14.63%)")
    print(f"  Reproduced R2:     {r2:.4f}   (Target: 0.9501)")
    print(f"  Reproduced MedAE:  {median_ae:.2f} kg/h  (Target: 129.31)")
    print(f"  Reproduced Bias:   {bias:.2f} kg/h  (Target: -141.82)")
    print("-" * 70)

    # Verification checks
    r2_diff = abs(r2 - 0.9501)
    mae_diff = abs(mae - 246.97)
    mape_diff = abs(mape - 14.63)

    if r2_diff < 0.001 and mae_diff < 0.1 and mape_diff < 0.1:
        print(">>> BASELINE REPRODUCTION STATUS: EXACT MATCH CONFIRMED (PASS) <<<")
        success = True
    else:
        print(f">>> DISCREPANCY DETECTED: delta_R2={r2_diff:.4f}, delta_MAE={mae_diff:.2f}, delta_MAPE={mape_diff:.2f} <<<")
        success = False

    return {
        "success": success,
        "r2": r2,
        "mae": mae,
        "rmse": rmse,
        "mape": mape,
        "median_ae": median_ae,
        "bias": bias,
        "train_time": train_time,
        "alpha": hybrid.alpha,
        "total_rows": total_rows,
    }


if __name__ == "__main__":
    res = run_baseline_reproduction()
    if not res["success"]:
        sys.exit(1)
