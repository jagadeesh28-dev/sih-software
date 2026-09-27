"""
Tamper-Evidence Verification Test Battery (Part F & Q).

Demonstrates that any unauthorized modification of an exported decision record (JSON or CSV)
causes cryptographic verification failure, and restoring the original restores verification pass.

Documented strictly as "TAMPER-EVIDENCE VERIFICATION", NOT "immutability proof".
"""

import json
import shutil
import tempfile
from pathlib import Path
import pytest

from src.export.decision_exporter import (
    build_optimization_decision_record,
    export_decision_package,
    verify_export_package
)

SAMPLE_JOB = {
    "job_id": "OPT-tamper999",
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
            "fuel_t": 145.2,
            "opex_usd": 94380.0,
            "wtw_tco2e": 450.1,
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
            }
        ],
        "evaluations": 2500,
        "runtime_s": 1.10
    }
}


@pytest.fixture
def export_env():
    """Setup a temporary export directory with a clean package."""
    tmp_dir = Path(tempfile.mkdtemp(prefix="eq_tamper_"))
    rec = build_optimization_decision_record("OPT-tamper999", SAMPLE_JOB, operator_status="CONFIRMED")
    pkg_dir = export_decision_package(rec, base_export_dir=tmp_dir, include_pareto=True)
    yield pkg_dir
    shutil.rmtree(tmp_dir, ignore_errors=True)


def test_tamper_evidence_json_modification_and_restoration(export_env):
    """
    TAMPER-EVIDENCE VERIFICATION:
    1. Verify initial clean package -> PASS
    2. Modify a single byte in decision_record.json -> FAIL
    3. Restore original content -> PASS
    """
    # 1. Initial verification must PASS
    v_init = verify_export_package(export_env)
    assert v_init["verified"] is True
    assert v_init["tampered"] is False
    assert v_init["status_label"] == "PASS: TAMPER-EVIDENCE VERIFIED"

    # 2. Modify one JSON value (alter fuel_t from 145.2 to 145.3)
    json_path = export_env / "decision_record.json"
    original_text = json_path.read_text(encoding="utf-8")
    assert "145.2" in original_text

    tampered_text = original_text.replace("145.2", "145.3")
    json_path.write_text(tampered_text, encoding="utf-8")

    # Verification must FAIL
    v_tampered = verify_export_package(export_env)
    assert v_tampered["verified"] is False
    assert v_tampered["tampered"] is True
    assert v_tampered["status_label"] == "FAIL: ARTIFACT TAMPERED / MODIFIED"
    assert any("Hash mismatch on decision_record.json" in e for e in v_tampered["errors"])

    # 3. Restore original content
    json_path.write_text(original_text, encoding="utf-8")

    # Verification must PASS again
    v_restored = verify_export_package(export_env)
    assert v_restored["verified"] is True
    assert v_restored["tampered"] is False
    assert v_restored["status_label"] == "PASS: TAMPER-EVIDENCE VERIFIED"


def test_tamper_evidence_csv_modification_and_restoration(export_env):
    """
    TAMPER-EVIDENCE VERIFICATION FOR CSV:
    1. Verify initial clean package -> PASS
    2. Modify a single number in decision_record.csv -> FAIL
    3. Restore original content -> PASS
    """
    # 1. Initial verification must PASS
    v_init = verify_export_package(export_env)
    assert v_init["verified"] is True

    # 2. Modify one cell in CSV (byte-level to avoid OS newline conversions)
    csv_path = export_env / "decision_record.csv"
    original_csv = csv_path.read_bytes()
    assert b"145.2" in original_csv

    tampered_csv = original_csv.replace(b"145.2", b"145.99")
    csv_path.write_bytes(tampered_csv)

    # Verification must FAIL
    v_tampered = verify_export_package(export_env)
    assert v_tampered["verified"] is False
    assert v_tampered["tampered"] is True
    assert any("Hash mismatch on decision_record.csv" in e for e in v_tampered["errors"])

    # 3. Restore original content
    csv_path.write_bytes(original_csv)

    # Verification must PASS again
    v_restored = verify_export_package(export_env)
    assert v_restored["verified"] is True
    assert v_restored["tampered"] is False


def test_tamper_evidence_missing_artifact_detection(export_env):
    """Verify that removing an artifact from the package directory immediately flags tampering."""
    readme_path = export_env / "README.txt"
    backup_bytes = readme_path.read_bytes()
    readme_path.unlink()

    v_missing = verify_export_package(export_env)
    assert v_missing["verified"] is False
    assert v_missing["tampered"] is True
    assert any("Missing artifact: README.txt" in e for e in v_missing["errors"])

    # Restore file
    readme_path.write_bytes(backup_bytes)
    v_restored = verify_export_package(export_env)
    assert v_restored["verified"] is True


def test_tamper_evidence_manifest_modification_detection(export_env):
    """Verify that altering manifest.json itself is detected (e.g. invalid json or schema mismatch)."""
    manifest_path = export_env / "manifest.json"
    orig_manifest = manifest_path.read_text(encoding="utf-8")

    # Corrupt manifest json
    manifest_path.write_text(orig_manifest + "CORRUPTION", encoding="utf-8")
    v_bad = verify_export_package(export_env)
    assert v_bad["verified"] is False
    assert v_bad["tampered"] is True
    assert "FAIL: CORRUPTED MANIFEST JSON" in v_bad["status_label"]

    # Restore
    manifest_path.write_text(orig_manifest, encoding="utf-8")
    v_ok = verify_export_package(export_env)
    assert v_ok["verified"] is True
