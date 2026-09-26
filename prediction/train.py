"""
Model training pipeline orchestration.
Coordinates data splitting, physics baseline calculation, residual fitting, and artifact export.
"""

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from .residual_model import HybridResidualPredictor
from .quantile_model import QuantileUncertaintyPredictor


def train_hybrid_pipeline(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    feature_cols: list,
    target_col: str = "fuel_mass_flow_kg_h",
    vessel_type: str = "container_feeder",
) -> Tuple[HybridResidualPredictor, QuantileUncertaintyPredictor]:
    """Train hybrid model and quantile uncertainty model."""
    hybrid = HybridResidualPredictor(feature_cols=feature_cols, default_vessel_type=vessel_type)
    hybrid.fit(train_df, val_df=val_df, target_col=target_col)

    quantile = QuantileUncertaintyPredictor(feature_cols=feature_cols)
    quantile.fit(train_df, target_col=target_col, val_df=val_df)

    return hybrid, quantile
