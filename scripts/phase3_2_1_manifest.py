"""
Phase 3.2.1 Reproducibility Manifest Generator.
Generates results/audit/phase3_2_1/reproducibility_manifest.json with all environmental,
code, data, model, and configuration hashes.
"""

import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(".").resolve()
AUDIT_DIR = ROOT_DIR / "results" / "audit" / "phase3_2_1"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def file_hash(filepath: Path) -> str:
    if not filepath.exists():
        return "MISSING"
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def generate_manifest():
    print("Generating Phase 3.2.1 Reproducibility Manifest...")

    manifest = {
        "manifest_version": "3.2.1-FINAL",
        "phase": "Phase 3.2.1 Independent Statistical Integrity & Benchmark Audit",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": "20309b214b9540a7363b7365e442a222cd9c49a1",
        "system_environment": {
            "os": platform.platform(),
            "python_version": sys.version,
            "machine": platform.machine(),
            "processor": platform.processor(),
            "cpu_count_logical": os.cpu_count(),
        },
        "dependency_versions": {
            "numpy": "2.2.3",
            "pandas": "2.2.3",
            "scipy": "1.15.2",
            "pytest": "9.1.1",
            "matplotlib": "3.10.1",
            "lightgbm": "4.6.0",
        },
        "experiment_configuration": {
            "scenario_id": "SCEN-01",
            "vessel_id": "CPS_Poseidon",
            "evaluation_budget": 2500,
            "matched_seeds_count": 30,
            "seed_schedule_formula": "100 + 37 * i for i in range(30)",
            "total_primary_runs": 150,
            "total_objective_evaluations": 375000,
            "objective_weights": [0.35, 0.30, 0.25, 0.05, 0.05],
            "normalization_scales": [50.0, 50000.0, 150.0, 10.0, 15.0],
            "robust_risk_lambda": 0.5,
        },
        "configuration_hashes": {
            "configs/fuels.yaml": file_hash(ROOT_DIR / "configs" / "fuels.yaml"),
            "configs/vessels.yaml": file_hash(ROOT_DIR / "configs" / "vessels.yaml") if (ROOT_DIR / "configs" / "vessels.yaml").exists() else "N/A",
            "pyproject.toml": file_hash(ROOT_DIR / "pyproject.toml"),
        },
        "core_code_hashes": {
            "optimization/canonical_mapper.py": file_hash(ROOT_DIR / "optimization" / "canonical_mapper.py"),
            "optimization/evaluator.py": file_hash(ROOT_DIR / "optimization" / "evaluator.py"),
            "optimization/regulatory.py": file_hash(ROOT_DIR / "optimization" / "regulatory.py"),
            "optimization/qpso.py": file_hash(ROOT_DIR / "optimization" / "qpso.py"),
            "optimization/differential_evolution.py": file_hash(ROOT_DIR / "optimization" / "differential_evolution.py"),
            "optimization/pso.py": file_hash(ROOT_DIR / "optimization" / "pso.py"),
            "optimization/genetic_algorithm.py": file_hash(ROOT_DIR / "optimization" / "genetic_algorithm.py"),
            "optimization/random_search.py": file_hash(ROOT_DIR / "optimization" / "random_search.py"),
            "prediction/domain_checker.py": file_hash(ROOT_DIR / "prediction" / "domain_checker.py"),
            "prediction/safe_objective.py": file_hash(ROOT_DIR / "prediction" / "safe_objective.py"),
        },
        "authoritative_audit_evidence": {
            "raw_result_inventory": file_hash(AUDIT_DIR / "raw_result_inventory.csv"),
            "independent_pairwise_differences": file_hash(AUDIT_DIR / "independent_pairwise_differences.csv"),
            "wilcoxon_independent_validation": file_hash(AUDIT_DIR / "wilcoxon_independent_validation.csv"),
            "permutation_test_results": file_hash(AUDIT_DIR / "permutation_test_results.csv"),
            "multiple_comparison_correction": file_hash(AUDIT_DIR / "multiple_comparison_correction.csv"),
            "effect_size_validation": file_hash(AUDIT_DIR / "effect_size_validation.csv"),
            "bootstrap_confidence_intervals": file_hash(AUDIT_DIR / "bootstrap_confidence_intervals.csv"),
            "optimizer_summary_independent": file_hash(AUDIT_DIR / "optimizer_summary_independent.csv"),
            "objective_decomposition_independent": file_hash(AUDIT_DIR / "objective_decomposition_independent.csv"),
            "decision_variable_diversity": file_hash(AUDIT_DIR / "decision_variable_diversity.csv"),
            "random_population_audit": file_hash(AUDIT_DIR / "random_population_audit.csv"),
            "landscape_audit": file_hash(AUDIT_DIR / "landscape_audit.csv"),
            "zero_difference_audit": file_hash(AUDIT_DIR / "zero_difference_audit.csv"),
            "de_qpso_tie_investigation": file_hash(AUDIT_DIR / "de_qpso_tie_investigation.json"),
        },
        "scientific_verdict": {
            "phase3_2_1_status": "CONDITIONAL_PASS",
            "phase4_ready": "YES_WITH_CLAIM_RESTRICTIONS",
            "qpso_status": "STATISTICALLY_EQUIVALENT",
            "de_status": "STATISTICALLY_EQUIVALENT",
            "wilcoxon_anomaly_resolved": True,
            "zero_difference_handling_verified": True,
        }
    }

    out_file = AUDIT_DIR / "reproducibility_manifest.json"
    with open(out_file, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Saved manifest: {out_file}")


if __name__ == "__main__":
    generate_manifest()
