"""
Unit & Integration Tests for Export Package Integrity and Security (Part A, M & Q).
Verifies package structure, manifest validation, API export endpoints, zip archives,
tamper verification, path traversal defenses, and secret sanitization.
"""

import io
import json
import shutil
import tempfile
import zipfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from api.main import app, JOBS, SCENARIOS
from src.export.decision_exporter import (
    build_optimization_decision_record,
    export_decision_package,
    verify_export_package,
    sanitize_filename,
    sanitize_payload,
    MANIFEST_SCHEMA_PATH,
    EXPORTS_DIR
)
import jsonschema

SAMPLE_JOB_DATA = {
    "job_id": "OPT-integ001",
    "status": "DONE",
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
            "fuel_t": 140.2,
            "opex_usd": 91200.0,
            "wtw_tco2e": 435.0,
            "delay_h": 0.0,
            "risk_cvar_excess": 0.0
        },
        "hard_violations": [],
        "vessels": [
            {
                "vessel_id": "CPS_Poseidon",
                "assigned_demand": "DEMAND_1",
                "cargo_tonnes": 5000.0,
                "speed_kn": 14.2,
                "fuel": "vlsfo",
                "shore_power": False
            }
        ],
        "evaluations": 2500,
        "runtime_s": 1.15
    },
    "recommendation_status": "PENDING_REVIEW"
}


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_package_structure_and_manifest_schema():
    """Verify package directory structure and manifest.json conformance."""
    rec = build_optimization_decision_record("OPT-integ001", SAMPLE_JOB_DATA, operator_status="CONFIRMED")
    tmp_dir = Path(tempfile.mkdtemp(prefix="eq_exp_test_"))
    try:
        pkg_dir = export_decision_package(rec, base_export_dir=tmp_dir, include_pareto=True)
        assert pkg_dir.exists() and pkg_dir.is_dir()

        required_files = [
            "decision_record.json",
            "decision_record.csv",
            "manifest.json",
            "README.txt",
            "calculation_summary.json"
        ]
        for rf in required_files:
            assert (pkg_dir / rf).exists(), f"Missing required file: {rf}"

        manifest_path = pkg_dir / "manifest.json"
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))

        # Check against manifest.schema.json
        assert MANIFEST_SCHEMA_PATH.exists()
        m_schema = json.loads(MANIFEST_SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.validate(instance=manifest_data, schema=m_schema)

        assert manifest_data["integrity_type"] == "TAMPER_EVIDENT_HASH_MANIFEST"
        assert len(manifest_data["artifacts"]) >= len(required_files)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_round_trip_json_fidelity():
    """Verify that exporting and re-reading JSON preserves exact numeric values."""
    rec = build_optimization_decision_record("OPT-integ001", SAMPLE_JOB_DATA, operator_status="CONFIRMED")
    tmp_dir = Path(tempfile.mkdtemp(prefix="eq_exp_test_"))
    try:
        pkg_dir = export_decision_package(rec, base_export_dir=tmp_dir, include_pareto=False)
        reloaded = json.loads((pkg_dir / "decision_record.json").read_text(encoding="utf-8"))

        assert reloaded["objectives"]["fuel_tonnes"] == rec["objectives"]["fuel_tonnes"]
        assert reloaded["objectives"]["operational_cost_usd"] == rec["objectives"]["operational_cost_usd"]
        assert reloaded["optimization"]["algorithm"] == "Hybrid_QI_A5"
        assert reloaded["optimization"]["seed"] == 1005
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_api_workflow_review_confirm_export(client):
    """Test full API operator progression: PENDING_REVIEW -> REVIEWED -> CONFIRMED -> EXPORTED."""
    job_id = "OPT-flow999"
    JOBS[job_id] = copy_job = dict(SAMPLE_JOB_DATA)
    copy_job["job_id"] = job_id
    copy_job["recommendation_status"] = "PENDING_REVIEW"

    # 1. Review
    rev = client.post(f"/api/recommendations/{job_id}/review")
    assert rev.status_code == 200
    assert rev.json()["recommendation_status"] == "REVIEWED"

    # 2. Confirm
    conf = client.post(
        f"/api/recommendations/{job_id}/confirm",
        json={"operator_id": "Capt. H. Nelson", "note": "All draft constraints validated."}
    )
    assert conf.status_code == 200
    assert conf.json()["recommendation_status"] == "CONFIRMED"

    # 3. Export
    exp = client.post(
        f"/api/recommendations/{job_id}/export",
        json={"operator_id": "Capt. H. Nelson", "note": "Exported approved plan.", "include_pareto": True}
    )
    assert exp.status_code == 200
    data = exp.json()
    assert data["status"] == "EXPORTED"
    rec_id = data["record_id"]
    assert rec_id.startswith("REC-OPT-")
    assert "download_urls" in data

    # 4. Verify via API
    ver = client.post(f"/api/exports/{rec_id}/verify")
    assert ver.status_code == 200
    ver_data = ver.json()
    assert ver_data["verified"] is True
    assert ver_data["tampered"] is False
    assert "TAMPER-EVIDENCE VERIFIED" in ver_data["status_label"]

    # 5. Download individual artifact
    dl_json = client.get(f"/api/exports/{rec_id}/download/decision_record.json")
    assert dl_json.status_code == 200
    assert dl_json.headers["content-type"].startswith("application/json")
    assert "REC-OPT-" in dl_json.text

    dl_csv = client.get(f"/api/exports/{rec_id}/download/decision_record.csv")
    assert dl_csv.status_code == 200
    assert dl_csv.headers["content-type"].startswith("text/csv")
    assert "record_id" in dl_csv.text

    # 6. Download ZIP archive
    arch = client.get(f"/api/exports/{rec_id}/archive")
    assert arch.status_code == 200
    assert arch.headers["content-type"] == "application/zip"
    zf = zipfile.ZipFile(io.BytesIO(arch.content))
    names = zf.namelist()
    assert "decision_record.json" in names
    assert "manifest.json" in names
    assert "README.txt" in names


def test_security_path_traversal_defense(client):
    """Verify that path traversal attempts in record_id or filename are strictly blocked."""
    # Attempt traversal in record_id
    bad_rec = client.get("/api/exports/../../etc/passwd/download/manifest.json")
    assert bad_rec.status_code in (400, 404)

    # Attempt traversal in filename
    bad_file = client.get("/api/exports/REC-OPT-integ001/download/../../secret.txt")
    assert bad_file.status_code in (400, 404)

    # Directly test sanitize_filename
    with pytest.raises(ValueError):
        sanitize_filename("../../etc/shadow")
    with pytest.raises(ValueError):
        sanitize_filename("..\\..\\boot.ini")
    with pytest.raises(ValueError):
        sanitize_filename("")


def test_security_secret_sanitization():
    """Verify that sanitize_payload removes any keys containing credential / token / key / secret."""
    dirty_dict = {
        "record_id": "REC-01",
        "api_key": "SUPER_SECRET_12345",
        "nested": {
            "auth_token": "BEARER_TOKEN_999",
            "password": "p@ssword",
            "safe_metric": 42.5
        }
    }
    clean = sanitize_payload(dirty_dict)
    assert "api_key" not in clean
    assert "auth_token" not in clean["nested"]
    assert "password" not in clean["nested"]
    assert clean["nested"]["safe_metric"] == 42.5
