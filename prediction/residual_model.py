r"""
Hybrid Physics + Machine Learning Residual Predictor.
Section 9 & 10:
$r_i = fuel_observed_i - fuel_physics_i$ (calculated strictly on TRAIN)
$\hat{r} = f_{ML}(X)$
$\hat{F}(x) = \max(0, F_{physics}(x) + \alpha \cdot \hat{r}(x))$

Primary alpha ablation grid: alpha in {0.0, 0.25, 0.50, 0.75, 1.00}
Tuned strictly on VALIDATION loss. TEST is never used in residual construction or tuning.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype
import lightgbm as lgb
from sklearn.metrics import mean_absolute_error

from .physics_predictor import PhysicsFuelPredictor
from .ml_baseline import CONFIG_A_FEATURES, CATEGORICAL_COLUMNS


class HybridResidualPredictor:
    """
    Physics-guided residual regressor combining theoretical naval architecture
    with data-driven corrections for hull fouling, unmodeled wave drift, and engine aging.
    """

    def __init__(
        self,
        physics_predictor: Optional[PhysicsFuelPredictor] = None,
        feature_cols: Optional[List[str]] = None,
        hyperparameters: Optional[Dict[str, Any]] = None,
        alpha: float = 1.0,
        default_vessel_type: str = "container_feeder",
        seed: int = 42,
    ):
        self.feature_cols = list(feature_cols) if feature_cols else list(CONFIG_A_FEATURES)
        self.alpha = float(alpha)
        self.seed = seed
        self.default_vessel_type = default_vessel_type

        self.physics = physics_predictor or PhysicsFuelPredictor(default_vessel_type=self.default_vessel_type)
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
        self.residual_model = lgb.LGBMRegressor(**self.params)
        self.training_metadata: Dict[str, Any] = {}
        self.categorical_dtypes: Dict[str, CategoricalDtype] = {}

    def _prepare_features(self, df: pd.DataFrame, is_train: bool = False) -> pd.DataFrame:
        """Apply categorical encodings learned strictly on TRAIN."""
        X = df[self.feature_cols].copy()
        for col in self.feature_cols:
            if col in CATEGORICAL_COLUMNS and col in X.columns:
                if is_train:
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
                if col in X.columns:
                    X[col] = pd.to_numeric(X[col], errors="coerce")
        return X

    def fit(
        self,
        train_df: pd.DataFrame,
        val_df: Optional[pd.DataFrame] = None,
        target_col: str = "fuel_mass_flow_kg_h",
        tune_alpha: bool = False,
        candidate_alphas: Optional[List[float]] = None,
        f_phys_train: Optional[np.ndarray] = None,
        f_phys_val: Optional[np.ndarray] = None,
    ) -> "HybridResidualPredictor":
        """
        1. Compute physics baseline on train_df (or use precomputed f_phys_train).
        2. Compute residual r = y_train - f_physics strictly on TRAIN.
        3. Fit LightGBM regressor on residual.
        4. Optionally sweep candidate alphas in {0.0, 0.25, 0.50, 0.75, 1.00} on val_df.
        """
        avail_features = [c for c in self.feature_cols if c in train_df.columns]
        if not avail_features:
            raise ValueError("None of the specified feature columns exist in train_df.")
        self.feature_cols = avail_features

        # 1. Physics baseline on TRAIN (using STW)
        if f_phys_train is None:
            f_phys_train = self.physics.predict(train_df)
        y_train = train_df[target_col].values
        # Strictly on TRAIN: r_i = F_observed_i - F_physics_i
        r_train = y_train - f_phys_train

        X_train = self._prepare_features(train_df, is_train=True)

        # 2. Validation set evaluation
        eval_set = None
        y_val = None
        if val_df is not None and target_col in val_df.columns:
            if f_phys_val is None:
                f_phys_val = self.physics.predict(val_df)
            y_val = val_df[target_col].values
            r_val = y_val - f_phys_val
            X_val = self._prepare_features(val_df, is_train=False)
            eval_set = [(X_val, r_val)]

        callbacks = [lgb.early_stopping(stopping_rounds=20, verbose=False)] if eval_set else None

        # 3. Fit ML on residual
        self.residual_model.fit(
            X_train,
            r_train,
            eval_set=eval_set,
            callbacks=callbacks,
        )

        # 4. Tune alpha strictly on validation data if requested
        best_alpha = self.alpha
        alpha_scores: Dict[float, float] = {}
        if tune_alpha and val_df is not None and f_phys_val is not None and y_val is not None:
            X_val_prep = self._prepare_features(val_df, is_train=False)
            r_hat_val = self.residual_model.predict(X_val_prep)
            # Primary controlled ablation grid per Section 9
            alphas_to_test = candidate_alphas or [0.0, 0.25, 0.50, 0.75, 1.00]
            best_val_mae = float("inf")

            for a in alphas_to_test:
                pred_val = np.maximum(0.0, f_phys_val + a * r_hat_val)
                score = float(mean_absolute_error(y_val, pred_val))
                alpha_scores[float(a)] = score
                if score < best_val_mae:
                    best_val_mae = score
                    best_alpha = float(a)

            self.alpha = best_alpha

        self.training_metadata = {
            "feature_columns": self.feature_cols,
            "feature_config": "CONFIG-B" if "vessel_id" in self.feature_cols else "CONFIG-A",
            "hyperparameters": self.params,
            "alpha": self.alpha,
            "alpha_sweep_scores": alpha_scores,
            "training_rows": len(train_df),
            "validation_rows": len(val_df) if val_df is not None else 0,
            "random_seed": self.seed,
            "best_iteration": getattr(self.residual_model, "best_iteration_", None),
        }
        return self

    def predict(self, df: pd.DataFrame, f_phys: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Predict fuel mass flow (kg/h):
        F_hat = max(0, F_physics + alpha * r_hat)
        """
        if f_phys is None:
            f_phys = self.physics.predict(df)
        X = self._prepare_features(df, is_train=False)
        r_hat = self.residual_model.predict(X)
        f_pred = f_phys + self.alpha * r_hat
        return np.maximum(0.0, f_pred)

