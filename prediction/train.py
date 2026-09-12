"""
Model training pipeline orchestration.
Coordinates data splitting, physics baseline calculation, residual fitting, and artifact export.
"""

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from .residual_model import HybridPhysicsMLPredictor
from .quantile_model import QuantileUncertaintyPredictor


def train_hybrid_pipeline(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    feature_cols: list,
    target_col: str = "fuel_flow",
    vessel_type: str = "container_feeder",
) -> Tuple[HybridPhysicsMLPredictor, QuantileUncertaintyPredictor]:
    """Train hybrid model and quantile uncertainty model."""
    y_train = train_df[target_col].values
    y_val = val_df[target_col].values

    hybrid = HybridPhysicsMLPredictor(vessel_type=vessel_type)
    hybrid.fit(train_df, y_train, feature_cols)

    quantile = QuantileUncertaintyPredictor()
    quantile.fit(train_df, y_train, feature_cols)

    return hybrid, quantile
