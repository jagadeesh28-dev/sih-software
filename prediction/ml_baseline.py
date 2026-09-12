"""
Pure Machine Learning Fuel Consumption Baseline (LightGBM).
Section 5 & 6:
- No unnecessary feature standardization (StandardScaler removed; tree splits are scale-invariant).
- Raw canonical numerical features used directly.
- Categorical features (vessel_type, fuel_type, vessel_id) explicitly handled via pandas Categorical dtypes
  fitted strictly on TRAIN to eliminate any validation/test data leakage.
- Defines CONFIG-A (without vessel_id, mandatory for cross-vessel generalization) and
  CONFIG-B (with vessel_id, restricted to ablation studies).
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype
import lightgbm as lgb

from common.logger import get_logger

logger = get_logger(__name__)

# CONFIG-A: Primary operational, environmental, and ship-type features EXCLUDING vessel_id.
# Mandatory for cross-vessel generalization to prevent memorizing specific vessel identities.
CONFIG_A_FEATURES = [
    "stw_kn",
    "sog_kn",
    "draft_m",
    "displacement_t",
    "rpm",
    "shaft_power_kw",
    "shaft_torque_nm",
    "engine_load_pct",
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

# CONFIG-B: Extended feature set INCLUDING vessel_id (used strictly for explicit memorization ablation).
CONFIG_B_FEATURES = CONFIG_A_FEATURES + ["vessel_id"]

CATEGORICAL_COLUMNS = ["vessel_type", "fuel_type", "vessel_id"]


class PureMLPredictor:
    """
    Data-driven gradient boosting regressor.
    Learns input-output mappings directly from observations without naval architecture models.
    Operates on raw canonical features with categorical encoding fitted strictly on TRAIN.
    """

    def __init__(
        self,
        feature_cols: Optional[List[str]] = None,
        hyperparameters: Optional[Dict[str, Any]] = None,
        seed: int = 42,
    ):
        self.feature_cols = list(feature_cols) if feature_cols else list(CONFIG_A_FEATURES)
        self.seed = seed
        self.params = hyperparameters or {
            "n_estimators": 150,
            "learning_rate": 0.05,
            "num_leaves": 31,
            "max_depth": 6,
            "min_child_samples": 20,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0,
            "random_state": self.seed,
            "n_jobs": -1,
            "verbose": -1,
        }
        self.model = lgb.LGBMRegressor(**self.params)
        self.training_metadata: Dict[str, Any] = {}
        # Stores categorical dtype categories learned strictly on TRAIN
        self.categorical_dtypes: Dict[str, CategoricalDtype] = {}

    def _prepare_features(self, df: pd.DataFrame, is_train: bool = False) -> pd.DataFrame:
        """
        Extract features and apply categorical dtypes.
        If is_train is True, learns categorical levels from df.
        Otherwise applies stored levels (unseen values map to NaN).
        """
        X = df[self.feature_cols].copy()
        for col in self.feature_cols:
            if col in CATEGORICAL_COLUMNS and col in X.columns:
                if is_train:
                    # Learn unique categories strictly from TRAIN
                    unique_cats = sorted([str(v) for v in X[col].dropna().unique()])
                    cat_type = CategoricalDtype(categories=unique_cats, ordered=False)
                    self.categorical_dtypes[col] = cat_type
                    X[col] = X[col].astype(str).astype(cat_type)
                else:
                    if col in self.categorical_dtypes:
                        X[col] = X[col].astype(str).astype(self.categorical_dtypes[col])
                    else:
                        X[col] = X[col].astype("category")
            else:
                # Canonical numerical features are kept raw (no StandardScaler)
                if col in X.columns:
                    X[col] = pd.to_numeric(X[col], errors="coerce")
        return X

    def fit(
        self,
        train_df: pd.DataFrame,
        val_df: Optional[pd.DataFrame] = None,
        target_col: str = "fuel_mass_flow_kg_h",
    ) -> "PureMLPredictor":
        """
        Train the model on train_df, using val_df strictly for early stopping / validation tracking.
        Categorical encodings and hyperparameters are fitted strictly on TRAIN.
        """
        # Feature availability filtering
        avail_features = [c for c in self.feature_cols if c in train_df.columns]
        if not avail_features:
            raise ValueError("None of the specified feature columns exist in train_df.")
        self.feature_cols = avail_features

        X_train = self._prepare_features(train_df, is_train=True)
        y_train = train_df[target_col].values

        eval_set = None
        if val_df is not None and target_col in val_df.columns:
            X_val = self._prepare_features(val_df, is_train=False)
            y_val = val_df[target_col].values
            eval_set = [(X_val, y_val)]

        callbacks = [lgb.early_stopping(stopping_rounds=20, verbose=False)] if eval_set else None

        self.model.fit(
            X_train,
            y_train,
            eval_set=eval_set,
            callbacks=callbacks,
        )

        self.training_metadata = {
            "feature_columns": self.feature_cols,
            "feature_config": "CONFIG-B" if "vessel_id" in self.feature_cols else "CONFIG-A",
            "hyperparameters": self.params,
            "training_rows": len(train_df),
            "validation_rows": len(val_df) if val_df is not None else 0,
            "random_seed": self.seed,
            "best_iteration": getattr(self.model, "best_iteration_", None),
            "feature_scaling": "NONE (Raw canonical numerical features per Section 5)",
        }
        return self

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Predict fuel consumption rate in kg/h."""
        X = self._prepare_features(df, is_train=False)
        preds = self.model.predict(X)
        # Fuel mass flow cannot physically be negative
        return np.maximum(0.0, preds)
