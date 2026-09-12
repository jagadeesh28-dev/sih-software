"""
Phase 0 Infrastructure Validation Tests.
Verifies configurations, evidence ledger, reproducibility, logging, and environment auditing.
"""

import sys
from pathlib import Path
import numpy as np
import pytest
import yaml

# Ensure sih26138_platform is on sys.path
pkg_root = Path(__file__).resolve().parent.parent
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

from common.config_loader import load_config, get_project_root
from common.reproducibility import set_seed, audit_environment
from common.logger import setup_logger


def test_project_root_detection():
    """Verify that get_project_root correctly locates the repository directory."""
    root = get_project_root()
    assert root.is_dir()
    assert (root / "pyproject.toml").is_file()
    assert (root / "requirements.txt").is_file()


def test_config_loading():
    """Verify that all external configuration YAML files exist and have required top-level keys."""
    physics_cfg = load_config("physics.yaml")
    assert "environment" in physics_cfg
    assert "hydrodynamics" in physics_cfg
    assert "propulsion" in physics_cfg
    assert "engine" in physics_cfg
    assert "reference_vessels" in physics_cfg

    fuels_cfg = load_config("fuels.yaml")
    assert "global_gwp_factors" in fuels_cfg
    assert "pathways" in fuels_cfg
    assert "vlsfo" in fuels_cfg["pathways"]
    assert "fossil_lng" in fuels_cfg["pathways"]

    opt_cfg = load_config("optimization.yaml")
    assert "budget" in opt_cfg
    assert "objectives" in opt_cfg
    assert "algorithms" in opt_cfg
    assert "qpso" in opt_cfg["algorithms"]

    scen_cfg = load_config("scenarios.yaml")
    assert "weather_scenarios" in scen_cfg
    assert "carbon_price_sweep" in scen_cfg
    assert "regulatory_standards" in scen_cfg

    bench_cfg = load_config("benchmark.yaml")
    assert "budget" in bench_cfg
    assert "algorithms_to_compare" in bench_cfg
    assert "statistical_tests" in bench_cfg


def test_evidence_claims_ledger():
    """Verify that evidence claims ledger follows strict epistemic schema."""
    claims_cfg = load_config("claims.yaml")
    assert "claims" in claims_cfg
    valid_types = {"FACT", "TARGET", "MEASURED_RESULT", "ASSUMPTION", "HYPOTHESIS", "LITERATURE_RESULT"}

    for claim in claims_cfg["claims"]:
        assert "claim_id" in claim
        assert "claim" in claim
        assert "type" in claim
        assert claim["type"] in valid_types, f"Invalid claim type: {claim['type']} in {claim['claim_id']}"
        assert "allowed_wording" in claim
        assert "forbidden_wording" in claim


def test_reproducibility_seed_determinism():
    """Verify that setting seeds yields deterministic random sequences."""
    set_seed(12345)
    seq1 = np.random.uniform(0.0, 1.0, size=10)

    set_seed(12345)
    seq2 = np.random.uniform(0.0, 1.0, size=10)

    np.testing.assert_allclose(seq1, seq2, err_msg="Seed setting failed to produce deterministic random sequence.")


def test_environment_audit():
    """Verify that audit_environment captures runtime and dependency versions."""
    env = audit_environment()
    assert "python_version" in env
    assert "platform" in env
    assert "packages" in env
    assert env["packages"]["numpy"] != "not_installed"
    assert env["packages"]["scipy"] != "not_installed"
    assert env["packages"]["pandas"] != "not_installed"


def test_logger_initialization():
    """Verify structured logger creation without handler duplication."""
    logger = setup_logger("test_logger")
    assert logger.name == "test_logger"
    assert len(logger.handlers) >= 1
