"""
Quantile Uncertainty Predictor for Maritime Fuel Consumption.
Section 14:
- Direct fuel-flow quantile regression: q05(F|X), q50(F|X), q95(F|X).
- LightGBM pinball quantile loss regression for tau in {0.05, 0.50, 0.95}.
- Documented non-crossing procedure enforcing q05 <= q50 <= q95.
- Evaluates Prediction Interval Coverage Probability (PICP), Mean Prediction Interval Width (MPIW),
  coverage error, and pinball loss.
- Uses strict terminology: 'quantile-derived dispersion proxy' instead of variance.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype
import lightgbm as lgb

from .evaluate import evaluate_quantiles
from .ml_baseline import CONFIG_A_FEATURES, CATEGORICAL_COLUMNS


class QuantileUncertaintyPredictor:
    """
    Fits separate quantile regressors for tau = 0.05, 0.50, and 0.95 directly on fuel mass flow.
    Yields calibrated 90% prediction intervals with monotonic non-crossing sorting.
    """

    def __init__(
        self,
        quantiles: Optional[List[float]] = None,
        feature_cols: Optional[List[str]] = None,
        seed: int = 42,
    ):
        self.quantiles = quantiles or [0.05, 0.50, 0.95]
        self.feature_cols = list(feature_cols) if feature_cols else list(CONFIG_A_FEATURES)
        self.seed = seed
        self.models: Dict[float, lgb.LGBMRegressor] = {}
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
        target_col: str = "fuel_mass_flow_kg_h",
        val_df: Optional[pd.DataFrame] = None,
    ) -> "QuantileUncertaintyPredictor":
        """
        Train pinball loss models for each target quantile directly on train_df.
        """
        avail_features = [c for c in self.feature_cols if c in train_df.columns]
        if not avail_features:
            raise ValueError("No matching feature columns found in train_df.")
        self.feature_cols = avail_features

        X_train = self._prepare_features(train_df, is_train=True)
        y_train = train_df[target_col].values

        for q in self.quantiles:
            model = lgb.LGBMRegressor(
                objective="quantile",
                alpha=q,
                n_estimators=120,
                learning_rate=0.05,
                num_leaves=31,
                max_depth=6,
                random_state=self.seed,
                n_jobs=-1,
                verbose=-1,
            )
            eval_set = [(self._prepare_features(val_df, is_train=False), val_df[target_col].values)] if val_df is not None else None
            callbacks = [lgb.early_stopping(stopping_rounds=15, verbose=False)] if eval_set else None

            model.fit(X_train, y_train, eval_set=eval_set, callbacks=callbacks)
            self.models[q] = model

        return self

    def predict_quantiles(self, df: pd.DataFrame) -> Dict[str, np.ndarray]:
        """
        Predict q05, q50, q95 and enforce documented non-crossing sorting.
        """
        X = self._prepare_features(df, is_train=False)
        raw_preds = {q: self.models[q].predict(X) for q in self.quantiles}

        q05 = np.maximum(0.0, raw_preds[0.05])
        q50 = np.maximum(0.0, raw_preds[0.50])
        q95 = np.maximum(0.0, raw_preds[0.95])

        # Enforce monotonic quantile order to prevent crossing: q05 <= q50 <= q95
        q50_adj = np.maximum(q05, q50)
        q95_adj = np.maximum(q50_adj, q95)

        # Quantile-derived dispersion proxy (q95 - q05)
        dispersion_proxy = q95_adj - q05

        return {
            "q05": q05,
            "q50": q50_adj,
            "q95": q95_adj,
            "quantile_derived_dispersion_proxy": dispersion_proxy,
        }

    def evaluate(self, df: pd.DataFrame, target_col: str = "fuel_mass_flow_kg_h") -> Dict[str, float]:
        """
        Evaluate empirical coverage and interval metrics against true observations.
        """
        y_true = df[target_col].values
        q_preds = self.predict_quantiles(df)
        return evaluate_quantiles(
            y_true=y_true,
            q05=q_preds["q05"],
            q50=q_preds["q50"],
            q95=q_preds["q95"],
        )
