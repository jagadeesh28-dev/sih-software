"""
Fresh inference reproduction of the frozen prediction metrics.

Loads the three committed LightGBM boosters, rebuilds the 60/20/20 forward temporal
test split from the processed parquet files, recomputes the physics baseline, and
returns test-split MAE / R2 plus split-conformal PICP / MPIW. Nothing is retrained:
this reproduces the *inference* results of the frozen models, not the training runs.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

import lightgbm as lgb
import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from prediction.physics_predictor import PhysicsFuelPredictor  # noqa: E402
from src.qi_prediction.validation import ValidationHarness  # noqa: E402

DATA_DIR = REPO_ROOT / "data" / "processed" / "real" / "fuelcast"
MODELS_DIR = REPO_ROOT / "models"
VESSELS = ["CPS_Poseidon", "CPS_Triton", "OSS_Ceto"]
TARGET = "fuel_mass_flow_kg_h"
V_CATS = ["offshore_supply", "passenger_cruise", "passenger_cruise_small"]
F_CATS = ["mgo", "vlsfo"]
MODELS = {
    "MODEL-REAL-04": ("model_real_04.txt", "model_real_04_meta.json"),
    "QI-C1": ("qi_c1.txt", "qi_c1_meta.json"),
    "QI-C1-vessel-type": ("qi_c1_vessel_type.txt", "qi_c1_vessel_type_meta.json"),
}


def compute_fresh_metrics() -> Dict[str, Any]:
    dfs = {v: pd.read_parquet(DATA_DIR / f"{v}.parquet") for v in VESSELS}
    _, _, test = ValidationHarness.forward_temporal_splits(dfs)
    f_phys = PhysicsFuelPredictor().predict(test)
    y = test[TARGET].to_numpy()
    with open(MODELS_DIR / "conformal_quantiles.json") as f:
        conformal = json.load(f)

    out: Dict[str, Any] = {"test_rows": int(len(test))}
    for name, (model_file, meta_file) in MODELS.items():
        booster = lgb.Booster(model_file=str(MODELS_DIR / model_file))
        X = test[booster.feature_name()].copy()
        if "vessel_type" in X:
            X["vessel_type"] = X["vessel_type"].astype(CategoricalDtype(V_CATS))
        if "fuel_type" in X:
            X["fuel_type"] = X["fuel_type"].astype(CategoricalDtype(F_CATS))
        pred = np.maximum(0.0, f_phys + booster.predict(X))
        err = y - pred
        mae = float(np.mean(np.abs(err)))
        r2 = float(1.0 - np.sum(err**2) / np.sum((y - y.mean()) ** 2))
        q = float(conformal[name]["0.9"]["q_val"])
        picp = float(np.mean((y >= np.maximum(0.0, pred - q)) & (y <= pred + q)) * 100.0)
        with open(MODELS_DIR / meta_file) as f:
            meta = json.load(f)
        out[name] = {
            "num_trees": booster.num_trees(),
            "fresh_test_mae_kg_h": round(mae, 4),
            "fresh_test_r2": round(r2, 6),
            "reference_test_mae_kg_h": meta.get("test_mae_kg_h"),
            "reference_test_r2": meta.get("test_r2"),
            "fresh_picp_90_pct": round(picp, 4),
            "reference_picp_90_pct": conformal[name]["0.9"].get("empirical_test_coverage_pct"),
            "mpiw_90_kg_h": round(2.0 * q, 2),
        }
    return out


if __name__ == "__main__":
    print(json.dumps(compute_fresh_metrics(), indent=2))
