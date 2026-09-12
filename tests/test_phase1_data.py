"""
Unit and Integration Tests for Phase 1 Data Engine.
Section 18: Validates schema contract, unit normalization, data quality auditor,
and leakage-safe partition operators (chronological, leave-vessel-out, sister-vessel grouping).
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

pkg_root = Path(__file__).resolve().parent.parent
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

from data.schemas import CANONICAL_SCHEMA, REQUIRED_FIELDS
from data.normalization import UnitNormalizationEngine
from data.data_quality import DataQualityAuditor
from data.splitting import LeakageSafeSplitter
from data.synthetic_generator import generate_synthetic_maritime_dataset


def test_canonical_schema_integrity():
    """Verify canonical schema definition contains 25 required fields with ranges and units."""
    assert len(REQUIRED_FIELDS) >= 25
    fields = CANONICAL_SCHEMA["fields"]
    for f_name in ["timestamp", "vessel_id", "sog_kn", "shaft_power_kw", "fuel_mass_flow_kg_h", "wave_height_m"]:
        assert f_name in fields
        assert "datatype" in fields[f_name]
        assert "physical_unit" in fields[f_name]
        assert "description" in fields[f_name]


def test_deterministic_unit_normalization():
    """Verify unit conversions produce correct canonical values and log audit records."""
    norm = UnitNormalizationEngine()

    # 1. Speed: 10 m/s to knots
    knots_val, rec1 = norm.convert_value(10.0, "speed", "m_s", field_name="speed_test")
    assert knots_val == pytest.approx(19.43844, rel=1e-4)
    assert rec1.canonical_unit == "knots"
    assert "1.943844" in rec1.conversion_rule

    # 2. Power: 5000000 W to kW
    kw_val, rec2 = norm.convert_value(5000000.0, "power", "w", field_name="power_test")
    assert kw_val == pytest.approx(5000.0)
    assert rec2.canonical_unit == "kW"

    # 3. Fuel flow: 24 tonnes/day to kg/h -> 24000 / 24 = 1000 kg/h
    fuel_val, rec3 = norm.convert_value(24.0, "fuel_flow", "tonnes_day", field_name="fuel_test")
    assert fuel_val == pytest.approx(1000.0)

    # 4. Ambiguous / unsupported unit rejection
    with pytest.raises(ValueError):
        norm.convert_value(100.0, "speed", "furlongs_per_fortnight")

    # Audit trail verification
    audit_df = norm.get_audit_trail()
    assert len(audit_df) == 3
    assert set(audit_df["field_name"]) == {"speed_test", "power_test", "fuel_test"}


def test_data_quality_auditor_anomaly_detection():
    """Verify auditor detects injected anomalies and classifies rows without data destruction."""
    df_synth = generate_synthetic_maritime_dataset(n_records=300, seed=123, inject_anomalies=True)
    auditor = DataQualityAuditor()
    res = auditor.audit_dataset(df_synth)

    summary = res["summary"]
    cls = summary["classifications"]

    # Must classify into 4 categories
    assert cls["VALID"]["count"] > 0
    assert cls["INVALID"]["count"] > 0
    assert cls["MISSING"]["count"] > 0

    # Total rows must be perfectly preserved
    assert sum(c["count"] for c in cls.values()) == len(df_synth)

    # Range violations detected
    assert len(res["range_violations"]) > 0

    # Duplicate rows detected
    assert summary["duplicate_count"] > 0


def test_chronological_temporal_split():
    """Verify strictly monotonic chronological split without temporal leakage or shuffling."""
    df_synth = generate_synthetic_maritime_dataset(n_records=300, seed=123, inject_anomalies=False)
    splitter = LeakageSafeSplitter(train_ratio=0.70, val_ratio=0.15, test_ratio=0.15)
    train_df, val_df, test_df = splitter.temporal_split(df_synth)

    assert len(train_df) + len(val_df) + len(test_df) == len(df_synth)

    t_train_max = pd.to_datetime(train_df["timestamp"]).max()
    t_val_min = pd.to_datetime(val_df["timestamp"]).min()
    t_val_max = pd.to_datetime(val_df["timestamp"]).max()
    t_test_min = pd.to_datetime(test_df["timestamp"]).min()

    assert t_train_max <= t_val_min
    assert t_val_max <= t_test_min


def test_leave_vessel_out_split():
    """Verify leave-vessel-out creates completely disjoint vessel sets."""
    df_synth = generate_synthetic_maritime_dataset(n_records=300, seed=123, inject_anomalies=False)
    splitter = LeakageSafeSplitter()
    train_df, test_df = splitter.leave_vessel_out_split(df_synth, holdout_vessel_id="VESSEL_HM_03")

    train_vessels = set(train_df["vessel_id"].unique())
    test_vessels = set(test_df["vessel_id"].unique())

    assert "VESSEL_HM_03" not in train_vessels
    assert test_vessels == {"VESSEL_HM_03"}
    assert train_vessels.isdisjoint(test_vessels)


def test_sister_vessel_group_isolation():
    """Verify sister vessels stay together in the same split partition."""
    df_synth = generate_synthetic_maritime_dataset(n_records=300, seed=123, inject_anomalies=False)
    sister_mapping = {
        "VESSEL_FE_01": "CLASS_FEEDER_1000",
        "VESSEL_FE_02": "CLASS_FEEDER_1000",
        "VESSEL_HM_03": "CLASS_HANDYMAX_50K",
    }
    splitter = LeakageSafeSplitter()
    train_df, test_df = splitter.sister_group_split(
        df_synth,
        sister_group_mapping=sister_mapping,
        holdout_group_id="CLASS_HANDYMAX_50K",
    )

    train_vessels = set(train_df["vessel_id"].unique())
    test_vessels = set(test_df["vessel_id"].unique())

    # Sister vessels 01 and 02 must BOTH be in train_vessels and NOT in test_vessels
    assert train_vessels == {"VESSEL_FE_01", "VESSEL_FE_02"}
    assert test_vessels == {"VESSEL_HM_03"}
    assert train_vessels.isdisjoint(test_vessels)
