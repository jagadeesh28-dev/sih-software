"""
Diagnostic Slicing and Error Analysis Engine.
Sections 16 & 17:
- Binned error analysis across operational and environmental variables:
  speed, draft, wind speed, wave height, engine load, vessel type, fuel type.
- Physics vs. ML vs. Hybrid diagnostic comparison identifying distinct failure and advantage regimes.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


class DiagnosticErrorAnalyzer:
    """
    Slices residuals across physical dimensions to detect non-linear degradation,
    under-prediction bias, and regime-specific model dominance.
    """

    @staticmethod
    def slice_by_bins(
        df: pd.DataFrame,
        y_true_col: str,
        y_pred_col: str,
        feature_col: str,
        bins: List[float],
        bin_labels: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Compute MAE, RMSE, and bias across user-specified bins of feature_col.
        """
        df_sliced = df.copy()
        if bin_labels is None:
            bin_labels = [f"[{bins[i]:.1f}, {bins[i+1]:.1f})" for i in range(len(bins) - 1)]

        df_sliced["_bin"] = pd.cut(df_sliced[feature_col], bins=bins, labels=bin_labels, include_lowest=True)

        rows = []
        for b in bin_labels:
            subset = df_sliced[df_sliced["_bin"] == b]
            n = len(subset)
            if n > 0:
                y_t = subset[y_true_col].values
                y_p = subset[y_pred_col].values
                mae = float(mean_absolute_error(y_t, y_p))
                rmse = float(np.sqrt(mean_squared_error(y_t, y_p)))
                bias = float(np.mean(y_p - y_t))
            else:
                mae, rmse, bias = np.nan, np.nan, np.nan

            rows.append({
                "feature": feature_col,
                "bin": b,
                "sample_count": n,
                "mae": mae,
                "rmse": rmse,
                "mean_bias": bias,
            })

        return pd.DataFrame(rows)

    @staticmethod
    def slice_by_category(
        df: pd.DataFrame,
        y_true_col: str,
        y_pred_col: str,
        cat_col: str,
    ) -> pd.DataFrame:
        """
        Compute MAE, RMSE, and bias across discrete categories (e.g. vessel_type, fuel_type).
        """
        rows = []
        for cat in df[cat_col].unique():
            subset = df[df[cat_col] == cat]
            n = len(subset)
            if n > 0:
                y_t = subset[y_true_col].values
                y_p = subset[y_pred_col].values
                mae = float(mean_absolute_error(y_t, y_p))
                rmse = float(np.sqrt(mean_squared_error(y_t, y_p)))
                bias = float(np.mean(y_p - y_t))
            else:
                mae, rmse, bias = np.nan, np.nan, np.nan

            rows.append({
                "category_column": cat_col,
                "category": str(cat),
                "sample_count": n,
                "mae": mae,
                "rmse": rmse,
                "mean_bias": bias,
            })
        return pd.DataFrame(rows)

    @classmethod
    def compare_physics_vs_ml(
        cls,
        df: pd.DataFrame,
        y_true_col: str,
        y_phys_col: str,
        y_ml_col: str,
        y_hybrid_col: str,
        slice_col: str = "stw_kn",
        bins: Optional[List[float]] = None,
    ) -> pd.DataFrame:
        """
        Direct regime comparison: calculates MAE for Physics, ML, and Hybrid in each bin,
        and declares the leading model per operating regime.
        """
        if bins is None:
            bins = [8.0, 12.0, 15.0, 18.0, 22.0]

        df_c = df.copy()
        df_c["_bin"] = pd.cut(df_c[slice_col], bins=bins, include_lowest=True)

        rows = []
        for b_val, grp in df_c.groupby("_bin", observed=False):
            if len(grp) == 0:
                continue
            y_t = grp[y_true_col].values
            mae_phys = float(mean_absolute_error(y_t, grp[y_phys_col].values))
            mae_ml = float(mean_absolute_error(y_t, grp[y_ml_col].values))
            mae_hyb = float(mean_absolute_error(y_t, grp[y_hybrid_col].values))

            # Determine winner
            maes = {"Physics": mae_phys, "ML": mae_ml, "Hybrid": mae_hyb}
            winner = min(maes, key=maes.get)

            rows.append({
                "bin": str(b_val),
                "samples": len(grp),
                "physics_mae": mae_phys,
                "ml_mae": mae_ml,
                "hybrid_mae": mae_hyb,
                "best_model": winner,
            })

        return pd.DataFrame(rows)

    @classmethod
    def generate_full_error_report(
        cls,
        df: pd.DataFrame,
        y_true_col: str,
        y_phys_col: str,
        y_ml_col: str,
        y_hybrid_col: str,
        output_dir: Optional[Path] = None,
    ) -> Dict[str, pd.DataFrame]:
        """
        Run complete sliced diagnostics across speed, draft, wind, wave, load, vessel_type.
        """
        results = {}

        # 1. Speed bins
        results["speed_bins"] = cls.slice_by_bins(
            df, y_true_col, y_hybrid_col, "stw_kn", bins=[8.0, 11.0, 14.0, 17.0, 22.0]
        )
        # 2. Wave height bins
        results["wave_bins"] = cls.slice_by_bins(
            df, y_true_col, y_hybrid_col, "wave_height_m", bins=[0.0, 1.0, 2.0, 3.5, 6.0]
        )
        # 3. Wind speed bins
        results["wind_bins"] = cls.slice_by_bins(
            df, y_true_col, y_hybrid_col, "wind_speed_ms", bins=[0.0, 5.0, 10.0, 15.0, 25.0]
        )
        # 4. Engine load bins
        results["load_bins"] = cls.slice_by_bins(
            df, y_true_col, y_hybrid_col, "engine_load_pct", bins=[0.0, 30.0, 60.0, 80.0, 100.0]
        )
        # 5. Vessel type categories
        if "vessel_type" in df.columns:
            results["vessel_categories"] = cls.slice_by_category(df, y_true_col, y_hybrid_col, "vessel_type")

        # 6. Regime comparison
        results["regime_comparison"] = cls.compare_physics_vs_ml(
            df, y_true_col, y_phys_col, y_ml_col, y_hybrid_col, slice_col="stw_kn"
        )

        if output_dir:
            out_p = Path(output_dir)
            out_p.mkdir(parents=True, exist_ok=True)
            for name, r_df in results.items():
                r_df.to_csv(out_p / f"{name}.csv", index=False)

        return results
