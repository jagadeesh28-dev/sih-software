"""
Unit & Integration Tests for Canonical Marine Decision Records (Part A & Q).
Validates JSON schema conformance, CSV derivative consistency, provenance, and data integrity.
"""

import csv
import io
import json
from pathlib import Path
import pytest
import jsonschema

from src.export.decision_exporter import (
    build_optimization_decision_record,
    build_scenario_decision_record,
    generate_decision_csv,
    generate_readme_text,
    generate_calculation_summary,
    canonical_json_bytes,
    sha256_bytes,
    DECISION_SCHEMA_PATH,
    MANIFEST_SCHEMA_PATH,
    SCHEMA_VERSION,
    CSV_COLUMNS
)

SAMPLE_JOB = {
    "job_id": "OPT-a1b2c3d4",
    "params": {
        "algorithm": "Hybrid_QI_A5",
        "seed": 1005,
        "budget": 2500,
        "weights": [0.35, 0.35, 0.30, 0.0, 0.0]
    },
    "result": {
        "feasible": True,
        "penalty_free": True,
        "penalty": 0.0,
        "soft_penalties": {},
        "objectives": {
            "fuel_t": 138.45,
            "opex_usd": 89950.0,
            "wtw_tco2e": 429.2,
            "delay_h": 0.0,
            "risk_cvar_excess": 0.0
        },
        "hard_violations": [],
        "vessels": [
            {
                "vessel_id": "CPS_Poseidon",
                "assigned_demand": "DEMAND_1",
                "cargo_tonnes": 5000.0,
                "speed_kn": 14.5,
                "fuel": "vlsfo",
                "shore_power": False
            },
            {
                "vessel_id": "CPS_Triton",
                "assigned_demand": "DEMAND_2",
                "cargo_tonnes": 12000.0,
                "speed_kn": 13.8,
                "fuel": "bio_methanol",
                "shore_power": True
            },
            {
                "vessel_id": "OSS_Ceto",
                "assigned_demand": None,
                "cargo_tonnes": 0.0,
                "speed_kn": 12.0,
                "fuel": "vlsfo",
                "shore_power": False
            }
        ],
        "evaluations": 2500,
        "runtime_s": 1.25
    }
}


def test_decision_record_schema_validation():
    """Verify that optimization decision record conforms strictly to Draft 2020-12 schema."""
    rec = build_optimization_decision_record("OPT-a1b2c3d4", SAMPLE_JOB, operator_status="CONFIRMED")
    assert DECISION_SCHEMA_PATH.exists()
    schema = json.loads(DECISION_SCHEMA_PATH.read_text(encoding="utf-8"))
    
    # Must not raise ValidationError
    jsonschema.validate(instance=rec, schema=schema)
    assert rec["record_metadata"]["record_id"] == "REC-OPT-a1b2c3d4"
    assert rec["record_metadata"]["schema_version"] == SCHEMA_VERSION
    assert rec["record_metadata"]["system"] == "EGREEN_QUANTA"


def test_scenario_record_schema_validation():
    """Verify that single voyage scenario decision record conforms strictly to Draft 2020-12 schema."""
    sample_scen = {
        "prediction": {
            "input": {
                "vessel_id": "CPS_Poseidon",
                "vessel_type": "passenger_cruise",
                "stw_kn": 14.5,
                "sog_kn": 14.5,
                "draft_m": 7.5,
                "displacement_t": 35000.0,
                "wind_speed_ms": 5.0,
                "wave_height_m": 1.0,
                "water_depth_m": 50.0
            },
            "result": {
                "fuel_prediction": 2540.2,
                "confidence": "HIGH",
                "model": "QI-C1-vessel-type",
                "model_version": "1.0.0-production",
                "uncertainty": {"lower_bound": 2350.0, "upper_bound": 2730.0}
            },
            "trust": {
                "state": "NORMAL",
                "ood_band": "IN_DOMAIN",
                "fallback_label": None,
                "envelope_distance": 0.15
            }
        },
        "voyage": {
            "fuel_type": "vlsfo",
            "voyage_hours": 20.0,
            "fuel_t": 50.8,
            "feasible": True,
            "cost": {"total_usd": 33020.0},
            "ghg": {"wtw_tco2e": 160.0},
            "schedule": {"delay_h": 0.0, "deadline_h": 24.0},
            "berth": {"source": "onboard_aux"}
        },
        "assumptions": {
            "fuel": {"price_usd_per_tonne": 650.0},
            "carbon_price_usd_per_tco2": 100.0,
            "demurrage_usd_per_h": 1500.0,
            "shore_power_tariff_usd_per_kwh": 0.18,
            "shore_power_connection_fee_usd": 250.0,
            "shore_power_grid_factor_g_co2e_per_kwh": 350.0,
            "fuels_config_sha256": "abcdef1234567890"
        },
        "basis": "VLSFO rate from model at scenario state"
    }

    rec = build_scenario_decision_record("SCEN-CPS_Poseidon-123456", sample_scen, operator_status="CONFIRMED")
    schema = json.loads(DECISION_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=rec, schema=schema)
    assert rec["record_metadata"]["record_type"] == "voyage_decision"
    assert rec["objectives"]["fuel_tonnes"] == 50.8


def test_real_fields_no_dummy_placeholders():
    """Verify that real model names, real vessel IDs, and real configs are embedded."""
    rec = build_optimization_decision_record("OPT-a1b2c3d4", SAMPLE_JOB, operator_status="CONFIRMED")
    
    # Provenance checks
    assert len(rec["provenance"]["model_artifacts"]) >= 3
    model_ids = [m["model_id"] for m in rec["provenance"]["model_artifacts"]]
    assert "qi_c1_vessel_type" in model_ids
    assert "model_real_04" in model_ids
    
    # Regulatory inputs
    reg_names = [r["framework"] for r in rec["provenance"]["regulatory_inputs"]]
    assert any("MEPC.391(81)" in r for r in reg_names)
    assert any("FuelEU" in r for r in reg_names)

    # Disclaimers
    assert "Advisory" in rec["decision"]["actuation_disclaimer"]
    assert "licensed marine officer" in rec["decision"]["actuation_disclaimer"]


def test_csv_derivative_consistency():
    """Verify that CSV derivative has correct header columns and preserves objective values."""
    rec = build_optimization_decision_record("OPT-a1b2c3d4", SAMPLE_JOB, operator_status="CONFIRMED")
    csv_text = generate_decision_csv(rec)
    
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = list(reader)
    
    assert len(rows) == len(SAMPLE_JOB["result"]["vessels"])
    for r in rows:
        assert r["record_id"] == "REC-OPT-a1b2c3d4"
        assert r["optimization_algorithm"] == "Hybrid_QI_A5"
        assert r["operator_status"] == "CONFIRMED"
        assert r["feasibility_status"] == "FEASIBLE"
    
    # First row contains total objectives
    assert float(rows[0]["fuel_tonnes"]) == pytest.approx(138.45, abs=0.01)
    assert float(rows[0]["operational_cost_usd"]) == pytest.approx(89950.0, abs=0.01)
    assert float(rows[0]["lifecycle_ghg_tco2e"]) == pytest.approx(429.2, abs=0.01)


def test_readme_and_calculation_summary_contents():
    """Verify that README.txt and calculation_summary.json provide complete self-description."""
    rec = build_optimization_decision_record("OPT-a1b2c3d4", SAMPLE_JOB, operator_status="CONFIRMED")
    readme = generate_readme_text(rec)
    
    assert "EGREEN QUANTA — MARINE OPERATOR DECISION RECORD" in readme
    assert "REC-OPT-a1b2c3d4" in readme
    assert "TAMPER-EVIDENCE & VERIFICATION INSTRUCTIONS" in readme
    assert "NOT class-certified" in readme
    assert "NOT IMO-approved" in readme
    
    summary = generate_calculation_summary(rec)
    assert summary["totals"]["fuel_tonnes"] == 138.45
    assert summary["totals"]["operational_cost_usd"] == 89950.0
    assert "IMO MEPC.391(81)" in summary["regulatory_frameworks"][0]
