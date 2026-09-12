"""
Baseline fuel prediction models:
1. Physics-only hydrodynamic predictor
2. Pure ML (unconstrained black-box) regressor
"""

import numpy as np
import pandas as pd
from typing import Optional
from sklearn.ensemble import HistGradientBoostingRegressor
from physics.resistance_model import VesselResistanceModel


class PhysicsOnlyPredictor:
    """Uses only theoretical naval architecture hydrodynamics without ML."""

    def __init__(self, vessel_type: str = "container_feeder"):
        self.physics = VesselResistanceModel(vessel_type=vessel_type)

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Predict fuel consumption rate (kg/h)."""
        preds = []
        for _, row in df.iterrows():
            res = self.physics.compute_total_resistance(
                speed_knots=float(row.get("stw", row.get("sog", 14.0))),
                wave_height_m=float(row.get("wave_height", 0.0)),
                wave_period_s=float(row.get("wave_period", 0.0)),
                wave_direction_deg=float(row.get("wave_direction", 0.0)),
                wind_speed_m_s=float(row.get("wind_speed", 0.0)),
                wind_direction_deg=float(row.get("wind_direction", 0.0)),
            )
            preds.append(res["fuel"]["total_fuel_kg_h"])
        return np.array(preds)


class PureMLBaselinePredictor:
    """Pure data-driven gradient boosting regressor without physics structure."""

    def __init__(self):
        self.model = HistGradientBoostingRegressor(random_state=42)
        self.feature_cols = []

    def fit(self, X: pd.DataFrame, y: np.ndarray, feature_cols: list):
        self.feature_cols = feature_cols
        self.model.fit(X[self.feature_cols], y)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict(X[self.feature_cols])
