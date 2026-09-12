"""
Comprehensive Data Quality Auditor.
Section 5 & 6: Checks A through P, classifies observations (VALID, SUSPICIOUS, INVALID, MISSING),
and generates full diagnostic artifacts without deleting any observations.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from .schemas import FIELD_DEFINITIONS, REQUIRED_FIELDS


class DataQualityAuditor:
    """
    Evaluates dataset integrity against physical constraints, schema definitions,
    and temporal continuity. Preserves raw records and tags them with quality flags.
    """

    CLASSIFICATION_PRIORITY = ["INVALID", "MISSING", "SUSPICIOUS", "VALID"]

    def __init__(self, schema_fields: Optional[Dict[str, Any]] = None):
        self.fields_cfg = schema_fields or FIELD_DEFINITIONS

    def audit_dataset(
        self,
        df: pd.DataFrame,
        output_dir: Optional[Path] = None,
        nominal_interval_seconds: float = 300.0,  # 5 min expected sampling
    ) -> Dict[str, Any]:
        """
        Run complete audit across all 16 quality dimensions.
        Returns dictionary of audit metrics and optionally writes artifacts.
        """
        n_rows = len(df)
        if n_rows == 0:
            return {"error": "Dataset is empty", "rows": 0}

        # Initialize per-row status tracking
        # Each row gets a set of issue tags
        row_issues: List[List[str]] = [[] for _ in range(n_rows)]
        row_classifications: List[str] = ["VALID"] * n_rows

        # --- A. Schema Validity ---
        missing_cols = [c for c in REQUIRED_FIELDS if c not in df.columns]
        extra_cols = [c for c in df.columns if c not in REQUIRED_FIELDS and c != "dataset_type"]

        # --- B & C. Missingness ---
        missingness_counts = {}
        for col in df.columns:
            cnt = int(df[col].isna().sum())
            missingness_counts[col] = {
                "missing_count": cnt,
                "missing_pct": (cnt / n_rows) * 100.0,
            }
            if cnt > 0:
                is_null = df[col].isna().values
                for idx in np.where(is_null)[0]:
                    row_issues[idx].append(f"MISSING_{col}")
                    if row_classifications[idx] != "INVALID":
                        row_classifications[idx] = "MISSING"

        missingness_df = pd.DataFrame.from_dict(missingness_counts, orient="index")

        # --- D. Duplicates ---
        duplicate_mask = df.duplicated().values
        duplicate_count = int(duplicate_mask.sum())
        duplicates_df = df[duplicate_mask].copy()
        for idx in np.where(duplicate_mask)[0]:
            row_issues[idx].append("DUPLICATE_ROW")
            row_classifications[idx] = "INVALID"

        # --- E & F. Timestamp Monotonicity & Gaps ---
        timestamp_gaps = []
        if "timestamp" in df.columns:
            try:
                ts = pd.to_datetime(df["timestamp"], errors="coerce")
                # Detect unparseable timestamps
                unparseable = ts.isna() & df["timestamp"].notna()
                for idx in np.where(unparseable)[0]:
                    row_issues[idx].append("INVALID_TIMESTAMP_FORMAT")
                    row_classifications[idx] = "INVALID"

                # Check per-vessel monotonicity
                vessels = df["vessel_id"].unique() if "vessel_id" in df.columns else ["all"]
                for v in vessels:
                    sub_mask = (df["vessel_id"] == v).values if "vessel_id" in df.columns else np.ones(n_rows, dtype=bool)
                    sub_indices = np.where(sub_mask)[0]
                    v_ts = ts.iloc[sub_indices]

                    # Check delta
                    deltas = v_ts.diff()
                    for pos, (i_prev, i_curr) in enumerate(zip(sub_indices[:-1], sub_indices[1:])):
                        sec = (v_ts.iloc[pos + 1] - v_ts.iloc[pos]).total_seconds()
                        if pd.notna(sec):
                            if sec < 0:
                                row_issues[i_curr].append("NON_MONOTONIC_TIMESTAMP")
                                row_classifications[i_curr] = "INVALID"
                            elif sec > (nominal_interval_seconds * 3.0):
                                gap_info = {
                                    "vessel_id": str(v),
                                    "start_index": int(i_prev),
                                    "end_index": int(i_curr),
                                    "gap_seconds": float(sec),
                                    "start_time": str(v_ts.iloc[pos]),
                                    "end_time": str(v_ts.iloc[pos + 1]),
                                }
                                timestamp_gaps.append(gap_info)
                                row_issues[i_curr].append(f"TIMESTAMP_GAP_{sec:.0f}s")
                                if row_classifications[i_curr] == "VALID":
                                    row_classifications[i_curr] = "SUSPICIOUS"
            except Exception as e:
                timestamp_gaps.append({"error": f"Timestamp processing failed: {e}"})

        timestamp_gaps_df = pd.DataFrame(timestamp_gaps)

        # --- G through O. Range Violations ---
        range_violations = []
        for col, cfg in self.fields_cfg.items():
            if col in df.columns and cfg.get("allowable_range") is not None:
                r_range = cfg["allowable_range"]
                dtype = cfg.get("datatype", "")

                # Timestamp temporal range bounds
                if col == "timestamp" and isinstance(r_range, list) and len(r_range) == 2:
                    t_min = pd.to_datetime(r_range[0])
                    t_max = pd.to_datetime(r_range[1])
                    for idx, val in enumerate(df[col]):
                        t_val = pd.to_datetime(val, errors="coerce")
                        if pd.notna(t_val) and (t_val < t_min or t_val > t_max):
                            row_issues[idx].append("OUT_OF_BOUNDS_timestamp")
                            row_classifications[idx] = "SUSPICIOUS"
                            range_violations.append({
                                "row_index": int(idx),
                                "column": col,
                                "value": str(val),
                                "min_allowed": str(r_range[0]),
                                "max_allowed": str(r_range[1]),
                                "severity": "SUSPICIOUS",
                            })

                # Categorical / string valid choices
                elif dtype in ["string", "category"] and isinstance(r_range, list):
                    allowed_set = set(r_range)
                    for idx, val in enumerate(df[col]):
                        if pd.notna(val) and str(val) not in allowed_set:
                            row_issues[idx].append(f"INVALID_CATEGORY_{col}")
                            row_classifications[idx] = "INVALID"
                            range_violations.append({
                                "row_index": int(idx),
                                "column": col,
                                "value": str(val),
                                "min_allowed": str(r_range),
                                "max_allowed": str(r_range),
                                "severity": "INVALID",
                            })

                # Numerical [min, max] bounds
                elif isinstance(r_range, list) and len(r_range) == 2 and isinstance(r_range[0], (int, float)):
                    r_min, r_max = r_range[0], r_range[1]
                    vals = pd.to_numeric(df[col], errors="coerce").values
                    out_of_bounds = (vals < r_min) | (vals > r_max)
                    bad_indices = np.where(out_of_bounds & ~np.isnan(vals))[0]
                    for idx in bad_indices:
                        val = vals[idx]
                        is_critical_violation = (
                            (col == "latitude" and (val < -90 or val > 90)) or
                            (col == "longitude" and (val < -180 or val > 180)) or
                            (col == "fuel_mass_flow_kg_h" and val < 0) or
                            (col == "shaft_power_kw" and val < 0) or
                            (col == "draft_m" and val < 0) or
                            (col == "wave_height_m" and val < 0)
                        )
                        tag = f"CRITICAL_OUT_OF_BOUNDS_{col}" if is_critical_violation else f"OUT_OF_BOUNDS_{col}"
                        row_issues[idx].append(tag)
                        if is_critical_violation:
                            row_classifications[idx] = "INVALID"
                        elif row_classifications[idx] == "VALID":
                            row_classifications[idx] = "SUSPICIOUS"

                        range_violations.append({
                            "row_index": int(idx),
                            "column": col,
                            "value": float(val),
                            "min_allowed": float(r_min),
                            "max_allowed": float(r_max),
                            "severity": "INVALID" if is_critical_violation else "SUSPICIOUS",
                        })

        range_violations_df = pd.DataFrame(range_violations)

        # --- P. Impossible Physical Combinations ---
        for idx in range(n_rows):
            row = df.iloc[idx]
            sog = float(row.get("sog_kn", 0.0)) if pd.notna(row.get("sog_kn")) else 0.0
            power = float(row.get("shaft_power_kw", 0.0)) if pd.notna(row.get("shaft_power_kw")) else 0.0
            fuel = float(row.get("fuel_mass_flow_kg_h", 0.0)) if pd.notna(row.get("fuel_mass_flow_kg_h")) else 0.0
            rpm = float(row.get("rpm", 0.0)) if pd.notna(row.get("rpm")) else 0.0
            load = float(row.get("engine_load_pct", 0.0)) if pd.notna(row.get("engine_load_pct")) else 0.0

            # 1. High speed with 0 power and 0 RPM (floating drift impossible at 20+ knots)
            if sog > 15.0 and power == 0.0 and rpm == 0.0:
                row_issues[idx].append("IMPOSSIBLE_COMBINATION: High SOG with zero propulsion")
                row_classifications[idx] = "INVALID"

            # 2. Fuel flow > 1500 kg/h with 0% engine load and 0 power
            if fuel > 1500.0 and load == 0.0 and power == 0.0:
                row_issues[idx].append("IMPOSSIBLE_COMBINATION: High fuel flow with zero engine load")
                row_classifications[idx] = "INVALID"

            # 3. RPM > 150 with power == 0
            if rpm > 120.0 and power == 0.0:
                row_issues[idx].append("IMPOSSIBLE_COMBINATION: High shaft RPM with zero power")
                if row_classifications[idx] == "VALID":
                    row_classifications[idx] = "SUSPICIOUS"

            # 4. Dimensionally Correct SOG / STW / Current Consistency (Patch Section 1)
            # A. Convert SOG and STW from knots to m/s (1 knot = 0.514444 m/s)
            stw_val = float(row.get("stw_kn", 0.0)) if pd.notna(row.get("stw_kn")) else None
            curr_spd_ms = float(row.get("current_speed_ms", 0.0)) if pd.notna(row.get("current_speed_ms")) else None
            curr_dir_deg = float(row.get("current_direction_deg", 0.0)) if pd.notna(row.get("current_direction_deg")) else None
            heading_deg = float(row.get("heading_deg", row.get("course_over_ground_deg", 65.0))) if (
                pd.notna(row.get("heading_deg")) or pd.notna(row.get("course_over_ground_deg"))
            ) else None

            # Physical non-negativity checks
            if stw_val is not None and stw_val < 0.0:
                row_issues[idx].append("INVALID_VELOCITY: STW < 0")
                row_classifications[idx] = "INVALID"

            if sog < 0.0:
                row_issues[idx].append("INVALID_VELOCITY: SOG < 0")
                row_classifications[idx] = "INVALID"

            if curr_spd_ms is not None and (curr_spd_ms < 0.0 or curr_spd_ms > 5.0):
                row_issues[idx].append(f"SUSPICIOUS_CURRENT: Impossible current magnitude ({curr_spd_ms:.2f} m/s)")
                if row_classifications[idx] == "VALID":
                    row_classifications[idx] = "SUSPICIOUS"

            if stw_val is not None and curr_spd_ms is not None and stw_val >= 0.0 and sog >= 0.0:
                # Dimensionally consistent conversion to m/s
                stw_ms = stw_val * 0.514444
                sog_ms = sog * 0.514444
                tolerance_ms = 1.5  # ~2.9 knots allowance for leeway drift, sensor dynamics, and wave action

                # B. If directional vectors are available, evaluate 2D vector triangle closure: V_ground = V_water + V_current
                if heading_deg is not None and curr_dir_deg is not None:
                    psi_rad = np.radians(heading_deg)
                    gamma_rad = np.radians(curr_dir_deg)
                    v_water_x = stw_ms * np.sin(psi_rad)
                    v_water_y = stw_ms * np.cos(psi_rad)
                    v_curr_x = curr_spd_ms * np.sin(gamma_rad)
                    v_curr_y = curr_spd_ms * np.cos(gamma_rad)
                    v_ground_exp_x = v_water_x + v_curr_x
                    v_ground_exp_y = v_water_y + v_curr_y
                    sog_exp_ms = np.hypot(v_ground_exp_x, v_ground_exp_y)
                    vector_residual_ms = abs(sog_ms - sog_exp_ms)

                    if vector_residual_ms > tolerance_ms:
                        row_issues[idx].append(
                            f"IMPLAUSIBLE_VECTOR_CLOSURE: Expected SOG={sog_exp_ms:.2f}m/s vs observed SOG={sog_ms:.2f}m/s (residual={vector_residual_ms:.2f}m/s)"
                        )
                        if row_classifications[idx] == "VALID":
                            row_classifications[idx] = "SUSPICIOUS"

                # C. Magnitude screening heuristic (triangle inequality: |SOG - STW| <= current_speed + tolerance)
                # Note limitation: Without full 3D/drift direction information, this serves as a screening heuristic.
                mag_diff_ms = abs(sog_ms - stw_ms)
                if mag_diff_ms > (curr_spd_ms + tolerance_ms):
                    row_issues[idx].append(
                        f"IMPLAUSIBLE_SOG_STW_CURRENT_MAGNITUDE: |SOG_ms - STW_ms|={mag_diff_ms:.2f}m/s exceeds current {curr_spd_ms:.2f}m/s + tol {tolerance_ms:.2f}m/s"
                    )
                    if row_classifications[idx] == "VALID":
                        row_classifications[idx] = "SUSPICIOUS"

        # Tally classification metrics
        valid_cnt = row_classifications.count("VALID")
        suspicious_cnt = row_classifications.count("SUSPICIOUS")
        invalid_cnt = row_classifications.count("INVALID")
        missing_cnt = row_classifications.count("MISSING")

        vessel_list = [str(v) for v in df["vessel_id"].unique()] if "vessel_id" in df.columns else ["UNKNOWN"]
        time_span = "UNKNOWN"
        if "timestamp" in df.columns and pd.to_datetime(df["timestamp"], errors="coerce").notna().any():
            t_clean = pd.to_datetime(df["timestamp"], errors="coerce").dropna()
            time_span = f"{t_clean.min().isoformat()} to {t_clean.max().isoformat()}"

        audit_summary = {
            "total_rows": n_rows,
            "unique_vessels": vessel_list,
            "vessel_count": len(vessel_list),
            "time_span": time_span,
            "nominal_sampling_interval_seconds": nominal_interval_seconds,
            "classifications": {
                "VALID": {"count": valid_cnt, "percentage": (valid_cnt / n_rows) * 100.0},
                "SUSPICIOUS": {"count": suspicious_cnt, "percentage": (suspicious_cnt / n_rows) * 100.0},
                "INVALID": {"count": invalid_cnt, "percentage": (invalid_cnt / n_rows) * 100.0},
                "MISSING": {"count": missing_cnt, "percentage": (missing_cnt / n_rows) * 100.0},
            },
            "duplicate_count": duplicate_count,
            "duplicate_percentage": (duplicate_count / n_rows) * 100.0,
            "timestamp_gaps_count": len(timestamp_gaps),
            "range_violations_count": len(range_violations),
            "missing_schema_columns": missing_cols,
            "extra_columns": extra_cols,
        }

        # Save artifacts if output_dir provided
        if output_dir:
            out_p = Path(output_dir)
            out_p.mkdir(parents=True, exist_ok=True)

            with open(out_p / "dataset_summary.json", "w", encoding="utf-8") as f:
                json.dump(audit_summary, f, indent=2)

            with open(out_p / "quality_report.json", "w", encoding="utf-8") as f:
                json.dump(audit_summary, f, indent=2)

            missingness_df.to_csv(out_p / "missingness.csv")
            duplicates_df.to_csv(out_p / "duplicates.csv", index=False)
            range_violations_df.to_csv(out_p / "range_violations.csv", index=False)
            timestamp_gaps_df.to_csv(out_p / "timestamp_gaps.csv", index=False)

            # Generate markdown report
            md_content = self._generate_markdown_report(audit_summary)
            with open(out_p / "quality_report.md", "w", encoding="utf-8") as f:
                f.write(md_content)

        return {
            "summary": audit_summary,
            "row_classifications": row_classifications,
            "row_issues": row_issues,
            "missingness": missingness_df,
            "duplicates": duplicates_df,
            "range_violations": range_violations_df,
            "timestamp_gaps": timestamp_gaps_df,
        }

    def _generate_markdown_report(self, summary: Dict[str, Any]) -> str:
        """Render readable markdown quality audit report."""
        cls = summary["classifications"]
        return f"""# Maritime Dataset Quality Audit Report

## 1. Executive Summary
- **Total Records Audited**: {summary['total_rows']:,}
- **Vessel Count**: {summary['vessel_count']} ({', '.join(summary['unique_vessels'])})
- **Temporal Span**: {summary['time_span']}
- **Nominal Sampling Interval**: {summary['nominal_sampling_interval_seconds']} s

## 2. Epistemic Quality Classification
Every observation has been classified without destructive discarding:

| Classification | Record Count | Percentage | Definition |
| :--- | :--- | :--- | :--- |
| **VALID** | {cls['VALID']['count']:,} | {cls['VALID']['percentage']:.2f}% | Physically sound, non-duplicate, within allowable ranges |
| **SUSPICIOUS** | {cls['SUSPICIOUS']['count']:,} | {cls['SUSPICIOUS']['percentage']:.2f}% | Plausible but extreme or preceded by timestamp gap |
| **INVALID** | {cls['INVALID']['count']:,} | {cls['INVALID']['percentage']:.2f}% | Physically impossible (e.g. negative fuel/power, bad coordinates) |
| **MISSING** | {cls['MISSING']['count']:,} | {cls['MISSING']['percentage']:.2f}% | Missing one or more required sensor channels |

## 3. Diagnostic Breakdown
- **Duplicate Observations**: {summary['duplicate_count']:,} ({summary['duplicate_percentage']:.2f}%)
- **Range Violations Detected**: {summary['range_violations_count']:,}
- **Temporal Gaps Detected (>3x nominal interval)**: {summary['timestamp_gaps_count']:,}
- **Missing Schema Columns**: {', '.join(summary['missing_schema_columns']) if summary['missing_schema_columns'] else 'None (All canonical columns present)'}

## 4. Policy for Machine Learning Ingestion
- Only **VALID** records are permitted into model training and validation sets.
- **INVALID** records are isolated and logged in `range_violations.csv` and `duplicates.csv`.
- **SUSPICIOUS** records require explicit experimenter flagging before inclusion.
"""
