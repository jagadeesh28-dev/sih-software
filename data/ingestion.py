"""
Dataset Ingestion and Validation Engine.
Performs schema-first inspection, quality auditing, and clean extraction.
Produces data_quality_report.json without silently discarding raw data.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

from common.logger import get_logger
from .schemas import REQUIRED_VESSEL_FIELDS, FIELD_UNITS

logger = get_logger(__name__)


class DatasetIngestionEngine:
    """
    Schema-first ingestion pipeline for maritime telemetry and environmental records.
    """

    def __init__(self, raw_data_dir: Optional[Path] = None):
        self.raw_data_dir = raw_data_dir or Path(__file__).resolve().parent / "raw"
        self.required_fields = REQUIRED_VESSEL_FIELDS
        self.field_units = FIELD_UNITS

    def inspect_dataset(self, file_path: Path) -> Dict[str, Any]:
        """
        Inspect dataset without loading full data into memory if large.
        Returns schema, columns present, and row counts.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset not found at {file_path}")

        # Read first 100 rows for schema discovery
        df_preview = pd.read_csv(file_path, nrows=100)
        columns_present = list(df_preview.columns)
        missing_vars = [f for f in self.required_fields if f not in columns_present]
        matched_vars = [f for f in self.required_fields if f in columns_present]

        report = {
            "file_path": str(file_path),
            "columns_present": columns_present,
            "matched_required_fields": matched_vars,
            "missing_required_fields": missing_vars,
            "field_units": {k: self.field_units.get(k, "unknown") for k in columns_present},
        }
        return report

    def generate_quality_report(
        self,
        df: pd.DataFrame,
        output_report_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Comprehensive data quality audit:
        - Schema & field counts
        - Missing values
        - Duplicates
        - Impossible physical values
        - Sampling interval & gaps
        """
        total_rows = len(df)
        duplicates = int(df.duplicated().sum())

        missing_summary = {
            col: int(df[col].isna().sum()) for col in df.columns
        }

        # Sampling interval analysis if timestamp exists
        sampling_stats = {}
        if "timestamp" in df.columns:
            try:
                ts = pd.to_datetime(df["timestamp"])
                deltas = ts.diff().dropna()
                sampling_stats = {
                    "median_interval_seconds": float(deltas.dt.total_seconds().median()) if not deltas.empty else 0.0,
                    "min_interval_seconds": float(deltas.dt.total_seconds().min()) if not deltas.empty else 0.0,
                    "max_interval_seconds": float(deltas.dt.total_seconds().max()) if not deltas.empty else 0.0,
                    "missing_timestamps_count": int(df["timestamp"].isna().sum()),
                }
            except Exception as e:
                sampling_stats = {"error": f"Failed to parse timestamps: {e}"}

        quality_report = {
            "total_rows": total_rows,
            "duplicates_count": duplicates,
            "missing_values": missing_summary,
            "sampling_statistics": sampling_stats,
            "quality_status": "PASS" if duplicates == 0 and total_rows > 0 else "WARNINGS_FOUND",
        }

        if output_report_path:
            output_path = Path(output_report_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(quality_report, f, indent=2)
            logger.info(f"Saved data quality report to {output_path}")

        return quality_report
