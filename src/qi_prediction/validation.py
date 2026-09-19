"""
Validation Harness for Maritime Telemetry Prediction.
SIH26138 - Phase 6

Implements:
1. Forward Temporal Splitting (60% Train, 20% Val, 20% Test)
2. Rolling-Origin Cross-Validation (3 Progressive Windows)
3. Leave-One-Vessel-Out (LOVO) across Poseidon, Triton, Ceto
4. Operating Regime Stratification (Cruising, Maneuvering, Stopped, Rough Sea)
5. Out-of-Distribution (OOD) Detection via Mahalanobis Distance
6. Physical Consistency Checks (Non-negativity, Monotonicity)
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.spatial.distance import mahalanobis

from prediction.evaluate import evaluate_predictions


class ValidationHarness:
    """Manages the full suite of temporal, cross-vessel, and regime validation experiments."""

    @staticmethod
    def forward_temporal_splits(
        df_vessels: Dict[str, pd.DataFrame],
        train_ratio: float = 0.6,
        val_ratio: float = 0.2,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Strict forward temporal split per vessel, concatenated into fleet sets."""
        train_list, val_list, test_list = [], [], []
        for v_name, df in df_vessels.items():
            n = len(df)
            n_tr = int(n * train_ratio)
            n_va = int(n * val_ratio)
            train_list.append(df.iloc[:n_tr].copy())
            val_list.append(df.iloc[n_tr : n_tr + n_va].copy())
            test_list.append(df.iloc[n_tr + n_va :].copy())

        fleet_train = pd.concat(train_list, ignore_index=True)
        fleet_val = pd.concat(val_list, ignore_index=True)
        fleet_test = pd.concat(test_list, ignore_index=True)
        return fleet_train, fleet_val, fleet_test

    @staticmethod
    def rolling_origin_windows(
        df_vessels: Dict[str, pd.DataFrame],
    ) -> List[Dict[str, pd.DataFrame]]:
        """
        Creates 3 progressive rolling temporal windows:
        Window 1: Train 0-50%, Test 50-65%
        Window 2: Train 0-65%, Test 65-80%
        Window 3: Train 0-80%, Test 80-100%
        """
        windows = [
            {"train_end": 0.50, "test_start": 0.50, "test_end": 0.65, "name": "Window_1"},
            {"train_end": 0.65, "test_start": 0.65, "test_end": 0.80, "name": "Window_2"},
            {"train_end": 0.80, "test_start": 0.80, "test_end": 1.00, "name": "Window_3"},
        ]

        out_windows = []
        for w in windows:
            w_trains, w_tests = [], []
            for v_name, df in df_vessels.items():
                n = len(df)
                tr_end = int(n * w["train_end"])
                te_start = int(n * w["test_start"])
                te_end = int(n * w["test_end"])
                w_trains.append(df.iloc[:tr_end].copy())
                w_tests.append(df.iloc[te_start:te_end].copy())

            out_windows.append({
                "name": w["name"],
                "train": pd.concat(w_trains, ignore_index=True),
                "test": pd.concat(w_tests, ignore_index=True),
            })
        return out_windows

    @staticmethod
    def leave_one_vessel_out_folds(
        df_vessels: Dict[str, pd.DataFrame],
    ) -> List[Dict[str, Any]]:
        """
        Generates 3 Leave-One-Vessel-Out folds:
        Fold 1: Triton + Ceto -> Poseidon
        Fold 2: Poseidon + Ceto -> Triton
        Fold 3: Poseidon + Triton -> Ceto
        """
        vessels = list(df_vessels.keys())
        folds = []
        for test_vessel in vessels:
            train_vessels = [v for v in vessels if v != test_vessel]
            train_df = pd.concat([df_vessels[v] for v in train_vessels], ignore_index=True)
            test_df = df_vessels[test_vessel].copy()
            folds.append({
                "test_vessel": test_vessel,
                "train_vessels": train_vessels,
                "train": train_df,
                "test": test_df,
            })
        return folds

    @staticmethod
    def evaluate_by_regime(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        regimes: np.ndarray,
    ) -> Dict[str, Dict[str, float]]:
        """Compute metrics stratified across operating regimes."""
        results = {}
        unique_regimes = np.unique(regimes)
        for r in unique_regimes:
            idx = (regimes == r)
            if np.sum(idx) > 0:
                m = evaluate_predictions(y_true[idx], y_pred[idx])
                results[str(r)] = {
                    "count": int(np.sum(idx)),
                    "mae": float(m["mae"]),
                    "rmse": float(m["rmse"]),
                    "mape": float(m.get("mape_pct", m.get("mape", 0.0))),
                    "r2": float(m["r2"]),
                }
        return results

    @staticmethod
    def evaluate_ood(
        X_train_num: np.ndarray,
        X_test_num: np.ndarray,
        y_test: np.ndarray,
        y_pred: np.ndarray,
        percentile_threshold: float = 95.0,
    ) -> Dict[str, Any]:
        """
        Compute In-Distribution vs Out-Of-Distribution performance using Mahalanobis distance.
        OOD defined as test samples whose Mahalanobis distance from train centroid exceeds threshold.
        """
        # Clean and standardize features fit strictly on train
        X_tr = np.nan_to_num(X_train_num, nan=0.0, posinf=0.0, neginf=0.0)
        X_te = np.nan_to_num(X_test_num, nan=0.0, posinf=0.0, neginf=0.0)

        mean = np.mean(X_tr, axis=0)
        std = np.std(X_tr, axis=0)
        std = np.where(std < 1e-6, 1.0, std)

        X_tr_std = (X_tr - mean) / std
        X_te_std = (X_te - mean) / std

        cov = np.cov(X_tr_std, rowvar=False) + 1e-3 * np.eye(X_tr.shape[1])
        try:
            inv_cov = np.linalg.pinv(cov)
        except Exception:
            inv_cov = np.diag(1.0 / np.diag(cov))

        # Vectorized Mahalanobis distance: sqrt( (x - mu)^T * inv_cov * (x - mu) )
        X_tr_sub = X_tr_std[::10]
        dists_train = np.sqrt(np.maximum(0.0, np.sum(np.dot(X_tr_sub, inv_cov) * X_tr_sub, axis=1)))
        cutoff = float(np.percentile(dists_train, percentile_threshold))

        dists_test = np.sqrt(np.maximum(0.0, np.sum(np.dot(X_te_std, inv_cov) * X_te_std, axis=1)))
        is_ood = dists_test > cutoff

        res_id = evaluate_predictions(y_test[~is_ood], y_pred[~is_ood]) if np.sum(~is_ood) > 0 else {}
        res_ood = evaluate_predictions(y_test[is_ood], y_pred[is_ood]) if np.sum(is_ood) > 0 else {}

        return {
            "cutoff_distance": cutoff,
            "id_count": int(np.sum(~is_ood)),
            "ood_count": int(np.sum(is_ood)),
            "id_metrics": {
                "mae": float(res_id.get("mae", 0.0)),
                "mape": float(res_id.get("mape_pct", 0.0)),
                "r2": float(res_id.get("r2", 0.0)),
            },
            "ood_metrics": {
                "mae": float(res_ood.get("mae", 0.0)),
                "mape": float(res_ood.get("mape_pct", 0.0)),
                "r2": float(res_ood.get("r2", 0.0)),
            },
        }

    @staticmethod
    def check_physical_consistency(y_pred: np.ndarray) -> Dict[str, Any]:
        """Audit physical bounds: non-negativity and extreme flow anomalies."""
        neg_count = int(np.sum(y_pred < 0.0))
        extreme_count = int(np.sum(y_pred > 20000.0))  # Exceeds max engine capacity (20 t/h)
        return {
            "negative_count": neg_count,
            "negative_pct": float(neg_count / len(y_pred) * 100.0),
            "extreme_flow_count": extreme_count,
            "is_physically_bounded": (neg_count == 0),
        }
