"""
Maritime feature engineering for hydrodynamics and fuel prediction.
Transforms raw telemetry into physically meaningful features (Froude number, wave encounter frequency, apparent wind).
"""

import numpy as np
import pandas as pd
from typing import List, Optional


class MaritimeFeatureEngineer:
    """
    Constructs hydrodynamically informed features from raw telemetry.
    """

    def __init__(self, lwl_m: float = 133.0):
        self.lwl_m = lwl_m
        self.gravity = 9.80665

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features from input DataFrame."""
        return self.transform(df)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute hydrodynamic non-dimensional numbers and environmental projections."""
        out = df.copy()

        # Speed through water in m/s
        if "stw" in out.columns:
            out["stw_m_s"] = out["stw"] * 0.514444
            out["froude_number"] = out["stw_m_s"] / np.sqrt(self.gravity * self.lwl_m)

        # Apparent wind projections
        if "wind_speed" in out.columns and "wind_direction" in out.columns:
            wind_rad = np.radians(out["wind_direction"])
            out["wind_head_component"] = out["wind_speed"] * np.cos(wind_rad)
            out["wind_cross_component"] = out["wind_speed"] * np.sin(wind_rad)

        # Wave energy density proxy (Hs^2 * Tp)
        if "wave_height" in out.columns and "wave_period" in out.columns:
            out["wave_energy_proxy"] = (out["wave_height"] ** 2) * out["wave_period"]

        return out
