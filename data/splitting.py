"""
Leakage-Safe Dataset Splitting Engine.
Sections 7, 8, 9:
- Chronological temporal splitting (strictly monotonic, no shuffling)
- Leave-Vessel-Out (cross-vessel holdout)
- Sister-vessel group isolation (preventing operational contamination)
"""

from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


class LeakageSafeSplitter:
    """
    Enforces non-leaking data partition boundaries for maritime time-series.
    """

    def __init__(
        self,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
    ):
        if not np.isclose(train_ratio + val_ratio + test_ratio, 1.0):
            raise ValueError(f"Split ratios must sum to 1.0, got {train_ratio + val_ratio + test_ratio}")
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio

    def temporal_split(
        self,
        df: pd.DataFrame,
        timestamp_col: str = "timestamp",
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Chronological splitting: Sorts strictly by timestamp, then cuts into
        Train (earlier), Validation (middle), and Test (later).
        Zero random shuffling.
        """
        if timestamp_col not in df.columns:
            raise KeyError(f"Timestamp column '{timestamp_col}' missing from DataFrame.")

        # Sort chronologically
        df_sorted = df.sort_values(by=timestamp_col, ascending=True).copy()
        n = len(df_sorted)

        train_end = int(n * self.train_ratio)
        val_end = int(n * (self.train_ratio + self.val_ratio))

        train_df = df_sorted.iloc[:train_end].copy()
        val_df = df_sorted.iloc[train_end:val_end].copy()
        test_df = df_sorted.iloc[val_end:].copy()

        # Sanity check: Ensure max(train) <= min(val) <= max(val) <= min(test)
        t_train_max = pd.to_datetime(train_df[timestamp_col]).max()
        t_val_min = pd.to_datetime(val_df[timestamp_col]).min()
        t_val_max = pd.to_datetime(val_df[timestamp_col]).max()
        t_test_min = pd.to_datetime(test_df[timestamp_col]).min()

        assert t_train_max <= t_val_min, "Leakage detected: Train timestamp overlaps with validation!"
        assert t_val_max <= t_test_min, "Leakage detected: Validation timestamp overlaps with test!"

        return train_df, val_df, test_df

    def leave_vessel_out_split(
        self,
        df: pd.DataFrame,
        holdout_vessel_id: str,
        vessel_col: str = "vessel_id",
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Leave-Vessel-Out split:
        Training: All vessels EXCEPT holdout_vessel_id.
        Testing: Strictly holdout_vessel_id.
        """
        if vessel_col not in df.columns:
            raise KeyError(f"Vessel column '{vessel_col}' missing from DataFrame.")

        all_vessels = set(df[vessel_col].unique())
        if holdout_vessel_id not in all_vessels:
            raise ValueError(f"Holdout vessel '{holdout_vessel_id}' not found. Available: {all_vessels}")

        train_df = df[df[vessel_col] != holdout_vessel_id].copy()
        test_df = df[df[vessel_col] == holdout_vessel_id].copy()

        # Verify disjoint vessel sets
        train_vessels = set(train_df[vessel_col].unique())
        test_vessels = set(test_df[vessel_col].unique())
        assert train_vessels.isdisjoint(test_vessels), "Vessel leakage detected between train and test!"

        return train_df, test_df

    def sister_group_split(
        self,
        df: pd.DataFrame,
        sister_group_mapping: Dict[str, str],
        holdout_group_id: str,
        vessel_col: str = "vessel_id",
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Sister-Vessel Group-Aware split.
        Maps each vessel_id -> sister_group_id.
        Guarantees sister vessels stay entirely within the same partition,
        preventing operational event leakage between sister ships.
        """
        df_mapped = df.copy()
        df_mapped["_sister_group"] = df_mapped[vessel_col].map(sister_group_mapping)

        if df_mapped["_sister_group"].isna().any():
            unmapped = df_mapped[df_mapped["_sister_group"].isna()][vessel_col].unique()
            raise ValueError(f"Vessels missing sister group mapping: {unmapped}")

        all_groups = set(df_mapped["_sister_group"].unique())
        if holdout_group_id not in all_groups:
            raise ValueError(f"Holdout group '{holdout_group_id}' not found. Available: {all_groups}")

        train_df = df_mapped[df_mapped["_sister_group"] != holdout_group_id].drop(columns=["_sister_group"])
        test_df = df_mapped[df_mapped["_sister_group"] == holdout_group_id].drop(columns=["_sister_group"])

        # Check disjoint vessels
        train_v = set(train_df[vessel_col].unique())
        test_v = set(test_df[vessel_col].unique())
        assert train_v.isdisjoint(test_v), "Sister vessel group leakage detected!"

        return train_df, test_df
