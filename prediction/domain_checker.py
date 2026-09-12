"""
Operating Domain Checker & Validity Envelope Auditor.
Phase 2.2 Optimization Readiness Gate:
- Audits empirical feature distributions across the training partition.
- Computes feature bounding envelopes (min, max, percentiles, IQR, std, density).
- Classifies candidate operational states into IN_DOMAIN, NEAR_BOUNDARY, OUT_OF_DOMAIN, or PHYSICALLY_INVALID.
- Computes normalized multi-dimensional distance to the training envelope.
- Prevents silent extrapolation during downstream optimization.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd

from common.logger import get_logger
from .ml_baseline import CONFIG_A_FEATURES, CATEGORICAL_COLUMNS

logger = get_logger(__name__)

# Hard physical validity bounds for maritime vessel operations
PHYSICAL_VALIDITY_BOUNDS = {
    "stw_kn": (0.1, 32.0),
    "sog_kn": (0.0, 35.0),
    "shaft_power_kw": (0.0, 25000.0),
    "shaft_torque_nm": (0.0, 3000000.0),
    "rpm": (0.0, 250.0),
    "draft_m": (2.0, 22.0),
    "displacement_t": (500.0, 150000.0),
    "engine_load_pct": (0.0, 115.0),
    "wave_height_m": (0.0, 18.0),
    "wave_period_s": (1.0, 30.0),
    "wave_direction_deg": (0.0, 360.0),
    "wind_speed_ms": (0.0, 50.0),
    "wind_direction_deg": (0.0, 360.0),
    "current_speed_ms": (0.0, 6.0),
    "current_direction_deg": (0.0, 360.0),
    "water_depth_m": (5.0, 11000.0),
}


class DomainChecker:
    """
    Evaluates whether an operational query point lies inside the empirical training envelope,
    near the boundary, or in an ungrounded extrapolation regime.
    """

    def __init__(self, feature_cols: Optional[List[str]] = None):
        self.feature_cols = list(feature_cols) if feature_cols else list(CONFIG_A_FEATURES)
        self.numerical_cols = [c for c in self.feature_cols if c not in CATEGORICAL_COLUMNS]
        self.categorical_cols = [c for c in self.feature_cols if c in CATEGORICAL_COLUMNS]
        
        self.envelope_stats: Dict[str, Dict[str, float]] = {}
        self.valid_categories: Dict[str, List[str]] = {}
        self.is_fitted = False

    def fit(self, train_df: pd.DataFrame) -> "DomainChecker":
        """
        Derive statistical envelope strictly from the training partition.
        """
        for col in self.numerical_cols:
            if col in train_df.columns:
                series = pd.to_numeric(train_df[col], errors="coerce").dropna()
                p01, p05, p25, p50, p75, p95, p99 = np.percentile(series, [1, 5, 25, 50, 75, 95, 99])
                min_val = float(series.min())
                max_val = float(series.max())
                mean_val = float(series.mean())
                std_val = float(series.std(ddof=1)) if len(series) > 1 else 1.0
                iqr_val = float(p75 - p25)

                self.envelope_stats[col] = {
                    "min": min_val,
                    "max": max_val,
                    "p01": float(p01),
                    "p05": float(p05),
                    "p25": float(p25),
                    "median": float(p50),
                    "p75": float(p75),
                    "p95": float(p95),
                    "p99": float(p99),
                    "mean": mean_val,
                    "std": max(std_val, 1e-6),
                    "iqr": iqr_val,
                    "count": int(len(series)),
                }

        for col in self.categorical_cols:
            if col in train_df.columns:
                cats = sorted(train_df[col].dropna().astype(str).unique().tolist())
                self.valid_categories[col] = cats

        self.is_fitted = True
        logger.info(f"DomainChecker fitted on {len(self.envelope_stats)} numerical and {len(self.valid_categories)} categorical features.")
        return self

    def check_physical_sanity(self, point: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Verify hard physical plausibility rules.
        """
        violations = []
        for col, (min_b, max_b) in PHYSICAL_VALIDITY_BOUNDS.items():
            if col in point and point[col] is not None:
                val = float(point[col])
                if val < min_b or val > max_b:
                    violations.append(f"{col}={val:.2f} violates physical bounds [{min_b}, {max_b}]")

        # Specific physical correlation sanity checks
        if "stw_kn" in point and "shaft_power_kw" in point:
            stw = float(point["stw_kn"])
            pwr = float(point["shaft_power_kw"])
            if stw > 12.0 and pwr < 100.0:
                violations.append(f"Impossible physics: high speed stw={stw:.1f} kn with near-zero power pwr={pwr:.1f} kW")
            if stw < 2.0 and pwr > 5000.0:
                violations.append(f"Impossible physics: zero speed stw={stw:.1f} kn with massive propulsion power pwr={pwr:.1f} kW")

        return (len(violations) == 0, violations)

    def compute_envelope_distance(self, point: Dict[str, Any]) -> float:
        """
        Compute normalized Euclidean distance outside the training [min, max] bounding box.
        Distance = 0.0 inside the bounding box, > 0.0 when extrapolating.
        """
        if not self.is_fitted:
            raise RuntimeError("DomainChecker must be fitted before computing distance.")

        dist_sq = 0.0
        n_dim = 0
        for col, stats in self.envelope_stats.items():
            if col in point and point[col] is not None:
                val = float(point[col])
                span = max(stats["max"] - stats["min"], stats["std"])
                if val > stats["max"]:
                    delta = (val - stats["max"]) / span
                    dist_sq += delta ** 2
                elif val < stats["min"]:
                    delta = (stats["min"] - val) / span
                    dist_sq += delta ** 2
                n_dim += 1

        return float(np.sqrt(dist_sq / max(n_dim, 1)))

    def evaluate_point(self, point: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate domain membership for an operational state.
        Returns domain_status: 'IN_DOMAIN', 'NEAR_BOUNDARY', 'OUT_OF_DOMAIN', or 'PHYSICALLY_INVALID'.
        """
        if not self.is_fitted:
            raise RuntimeError("DomainChecker must be fitted before evaluating points.")

        # 1. Physical Sanity
        is_phys_sane, phys_violations = self.check_physical_sanity(point)
        if not is_phys_sane:
            return {
                "domain_status": "PHYSICALLY_INVALID",
                "envelope_distance": self.compute_envelope_distance(point),
                "reasons": phys_violations,
                "is_valid_candidate": False,
            }

        # 2. Categorical Validity
        cat_violations = []
        for col, valid_cats in self.valid_categories.items():
            if col in point and point[col] is not None:
                cat_val = str(point[col])
                if cat_val not in valid_cats:
                    cat_violations.append(f"Unknown category {col}='{cat_val}' (valid: {valid_cats})")

        if cat_violations:
            return {
                "domain_status": "OUT_OF_DOMAIN",
                "envelope_distance": self.compute_envelope_distance(point),
                "reasons": cat_violations,
                "is_valid_candidate": False,
            }

        # 3. Numerical Boundary & Percentile Checks
        ood_violations = []
        boundary_warnings = []

        for col, stats in self.envelope_stats.items():
            if col in point and point[col] is not None:
                val = float(point[col])
                # Out of empirical min-max bounds
                if val < stats["min"]:
                    ood_violations.append(f"{col}={val:.2f} < train_min ({stats['min']:.2f})")
                elif val > stats["max"]:
                    ood_violations.append(f"{col}={val:.2f} > train_max ({stats['max']:.2f})")
                # Near boundary (outside P01-P99 core empirical region)
                elif val < stats["p01"]:
                    boundary_warnings.append(f"{col}={val:.2f} below P01 ({stats['p01']:.2f})")
                elif val > stats["p99"]:
                    boundary_warnings.append(f"{col}={val:.2f} above P99 ({stats['p99']:.2f})")

        dist = self.compute_envelope_distance(point)

        if ood_violations:
            return {
                "domain_status": "OUT_OF_DOMAIN",
                "envelope_distance": dist,
                "reasons": ood_violations,
                "is_valid_candidate": False,
            }
        elif boundary_warnings:
            return {
                "domain_status": "NEAR_BOUNDARY",
                "envelope_distance": dist,
                "reasons": boundary_warnings,
                "is_valid_candidate": True,
            }
        else:
            return {
                "domain_status": "IN_DOMAIN",
                "envelope_distance": 0.0,
                "reasons": ["Operating state fully inside empirical P01-P99 envelope."],
                "is_valid_candidate": True,
            }

    def evaluate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Batch evaluation of DataFrame rows.
        """
        results = []
        for _, row in df.iterrows():
            res = self.evaluate_point(row.to_dict())
            results.append({
                "domain_status": res["domain_status"],
                "envelope_distance": res["envelope_distance"],
                "is_valid_candidate": res["is_valid_candidate"],
                "reason": "; ".join(res["reasons"]),
            })
        return pd.DataFrame(results, index=df.index)

    def get_domain_envelope(self) -> pd.DataFrame:
        """
        Return tabular summary of the fitted empirical domain envelope.
        """
        if not self.is_fitted:
            raise RuntimeError("DomainChecker not fitted.")

        rows = []
        for col, s in self.envelope_stats.items():
            rows.append({
                "feature": col,
                "min": s["min"],
                "p01": s["p01"],
                "p05": s["p05"],
                "median": s["median"],
                "p95": s["p95"],
                "p99": s["p99"],
                "max": s["max"],
                "mean": s["mean"],
                "std": s["std"],
                "iqr": s["iqr"],
                "observations": s["count"],
            })
        return pd.DataFrame(rows)
