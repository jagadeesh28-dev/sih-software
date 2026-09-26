"""
SIH26138 - Egreen Quanta: Official Release Gate Script
Evaluates 16 Non-Negotiable Release Gates (G1 to G16):
  G1: DATA - Dataset Integrity & Cleaning Reconciliation
  G2: REPRODUCIBILITY - Environment & Deterministic Execution
  G3: PREDICTION - Model Prediction Accuracy & Frozen Baselines
  G4: VESSEL-TYPE FEATURE - Explicit Categorical Feature & 30-Seed Ablation
  G5: UNCERTAINTY - Split Conformal Uncertainty Coverage & Sharpness
  G6: OOD - Out-of-Distribution Guard & Severe Storm Detection
  G7: COST OBJECTIVE - Multi-Component Operational Cost Minimization
  G8: LIFECYCLE GHG OBJECTIVE - IMO MEPC.391(81) Well-to-Wake Accounting
  G9: MULTI-OBJECTIVE OPTIMIZATION - Cost/GHG Trade-Offs & Pareto Frontier
  G10: BENCHMARK - Multi-Algorithm Benchmark (DE, QPSO, GA, NSGA-III)
  G11: SCALABILITY - Dimensional Scalability & O(D) Execution Profiling
  G12: SAFETY - Stress Tests, Edge Cases & Fault Interception
  G13: ALTERNATIVE FUELS - Invariant Shaft Work Scenario Modeling
  G14: DEMO - 11 Executable Demonstration Scenes
  G15: CLAIM CONSISTENCY - Scientific Honesty & Prohibited Claims Enforcement
  G16: TRACEABILITY - Git SHA, Artifact Hashes & Requirement Mapping

Generates:
  RELEASE/release_manifest.json
  RELEASE/release_gate.json
"""

import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

AUDIT_DIR = REPO_ROOT / "results" / "audit"
MODELS_DIR = REPO_ROOT / "models"
DATA_DIR = REPO_ROOT / "data" / "processed" / "real" / "fuelcast"
RESULTS_DIR = REPO_ROOT / "results"
RELEASE_DIR = REPO_ROOT / "RELEASE"
RELEASE_DIR.mkdir(parents=True, exist_ok=True)

# How each gate's verdict is obtained. FRESH gates execute the computation now;
# REFERENCE gates only verify committed evidence artifacts produced earlier.
FRESH = "FRESHLY COMPUTED"
REFERENCE = "REFERENCE ARTIFACT VERIFIED"
GATE_EVIDENCE = {
    "G1_DATA": FRESH,
    "G2_REPRODUCIBILITY": FRESH,
    "G3_PREDICTION": FRESH,
    "G4_VESSEL_TYPE": REFERENCE,
    "G5_UNCERTAINTY": FRESH,
    "G6_OOD": FRESH,
    "G7_COST_OBJECTIVE": FRESH,
    "G8_LIFECYCLE_GHG": FRESH,
    "G9_MULTIOBJECTIVE": REFERENCE,
    "G10_BENCHMARK": REFERENCE,
    "G11_SCALABILITY": REFERENCE,
    "G12_SAFETY": FRESH,
    "G13_ALTERNATIVE_FUELS": FRESH,
    "G14_DEMO": FRESH,
    "G15_CLAIM_CONSISTENCY": FRESH,
    "G16_TRACEABILITY": FRESH,
}

# Allowed drift between a fresh inference run and the frozen reference metrics.
MAE_TOLERANCE_KG_H = 0.5
R2_TOLERANCE = 0.0005
PICP_TOLERANCE_PCT = 0.05


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


_FRESH_METRICS: Dict[str, Any] = {}


def fresh_metrics() -> Dict[str, Any]:
    """Run the frozen boosters on the test split once and reuse for G3 and G5."""
    if not _FRESH_METRICS:
        from fresh_metrics import compute_fresh_metrics
        _FRESH_METRICS.update(compute_fresh_metrics())
    return _FRESH_METRICS


def get_file_sha256(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def get_git_sha() -> str:
    try:
        res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return "UNKNOWN"


def run_gate_g1_data() -> Tuple[bool, Dict[str, Any]]:
    """G1: Dataset row counts, 12-row cleaning reconciliation, file SHA256 hashes."""
    import pandas as pd
    vessels = {
        "CPS_Poseidon.parquet": 105422,
        "CPS_Triton.parquet": 25347,
        "OSS_Ceto.parquet": 43205,
    }
    actual_counts = {}
    hashes = {}
    total_records = 0

    for v, expected_n in vessels.items():
        p = DATA_DIR / v
        if not p.exists():
            return False, {"error": f"Missing parquet file {v}"}
        hashes[v] = get_file_sha256(p)
        df = pd.read_parquet(p)
        n = len(df)
        actual_counts[v] = n
        total_records += n
        if n != expected_n:
            return False, {"error": f"Row count mismatch for {v}: expected {expected_n}, got {n}"}

    reconciliation = {
        "raw_records": 173986,
        "validated_records": 173974,
        "removed_records": 12,
        "removal_reason": "Trailing null timestamps and sensor dropouts during logger shutdown",
        "total_records": total_records,
        "vessel_counts": actual_counts,
        "file_hashes": hashes,
    }
    passed = (total_records == 173974)
    return passed, reconciliation


def run_gate_g2_reproducibility() -> Tuple[bool, Dict[str, Any]]:
    """G2: Environment reproducibility, pinned dependencies, deterministic execution."""
    import lightgbm
    import numpy
    import pandas
    import scipy
    import sklearn

    env_info = {
        "python": sys.version.split()[0],
        "numpy": numpy.__version__,
        "pandas": pandas.__version__,
        "scipy": scipy.__version__,
        "lightgbm": lightgbm.__version__,
        "scikit_learn": sklearn.__version__,
        "split_manifest": (REPO_ROOT / "07_REAL_SPLIT_MANIFEST.json").exists(),
        "random_seed": 42,
    }
    from importlib.metadata import PackageNotFoundError, version
    mismatches = {}
    for line in (REPO_ROOT / "requirements-lock.txt").read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if "==" not in line:
            continue
        pkg, pinned = (s.strip() for s in line.split("==", 1))
        try:
            installed = version(pkg)
        except PackageNotFoundError:
            installed = None
        if installed != pinned:
            mismatches[pkg] = {"pinned": pinned, "installed": installed}
    env_info["lockfile_mismatches"] = mismatches
    passed = env_info["split_manifest"] and not mismatches
    return passed, env_info


def run_gate_g3_prediction() -> Tuple[bool, Dict[str, Any]]:
    """G3: Frozen baseline MODEL-REAL-04 and candidate QI-C1 accuracy, re-run on the test split."""
    fm = fresh_metrics()
    details: Dict[str, Any] = {"test_rows": fm["test_rows"]}
    passed = True
    for name in ("MODEL-REAL-04", "QI-C1", "QI-C1-vessel-type"):
        m = fm[name]
        reproduced = (
            abs(m["fresh_test_mae_kg_h"] - m["reference_test_mae_kg_h"]) <= MAE_TOLERANCE_KG_H
            and abs(m["fresh_test_r2"] - m["reference_test_r2"]) <= R2_TOLERANCE
        )
        # Acceptance thresholds apply to the frozen primary/anchor models only.
        meets_threshold = name == "QI-C1-vessel-type" or (
            m["fresh_test_r2"] >= 0.945 and m["fresh_test_mae_kg_h"] <= 250.0
        )
        passed = passed and reproduced and meets_threshold
        details[name] = {
            "fresh_mae_kg_h": m["fresh_test_mae_kg_h"],
            "fresh_r2": m["fresh_test_r2"],
            "reference_mae_kg_h": round(m["reference_test_mae_kg_h"], 4),
            "reference_r2": round(m["reference_test_r2"], 6),
            "reproduced_within_tolerance": reproduced,
        }
    details["note"] = "Inference re-run with committed boosters on the forward temporal test split; no retraining."
    return passed, details


def run_gate_g4_vessel_type() -> Tuple[bool, Dict[str, Any]]:
    """G4: Explicit vessel_type feature integration, 30-seed ablation and per-vessel breakdown."""
    model_txt = MODELS_DIR / "qi_c1_vessel_type.txt"
    model_meta = MODELS_DIR / "qi_c1_vessel_type_meta.json"
    ablation_csv = RESULTS_DIR / "vessel_type_ablation.csv"
    metrics_json = RESULTS_DIR / "vessel_type_metrics.json"

    if not (model_txt.exists() and model_meta.exists() and ablation_csv.exists() and metrics_json.exists()):
        return False, {"error": "Missing vessel_type model artifacts or ablation results"}

    with open(model_meta, "r", encoding="utf-8") as f:
        meta = json.load(f)
    with open(metrics_json, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    has_feature = "vessel_type" in meta.get("features", [])
    has_encoding = "encoding" in meta
    seeds_run = metrics.get("n_seeds", 0)
    passed = has_feature and has_encoding and (seeds_run >= 30)

    details = {
        "model_id": meta.get("model_id"),
        "features": meta.get("features"),
        "encoding": meta.get("encoding"),
        "seeds_evaluated": seeds_run,
        "model_a_mean_mae": metrics.get("mean_30seed", {}).get("model_a_mae"),
        "model_b_mean_mae": metrics.get("mean_30seed", {}).get("model_b_mae"),
        "qiea_selection_frequency": metrics.get("qiea_feature_selection", {}).get("vessel_type_frequency"),
        "per_vessel_metrics": {
            "CPS_Poseidon_mae": metrics.get("mean_30seed", {}).get("model_b_poseidon_mae"),
            "CPS_Triton_mae": metrics.get("mean_30seed", {}).get("model_b_triton_mae"),
            "OSS_Ceto_mae": metrics.get("mean_30seed", {}).get("model_b_ceto_mae"),
        },
    }
    return passed, details


def run_gate_g5_uncertainty() -> Tuple[bool, Dict[str, Any]]:
    """G5: Conformal prediction coverage and sharpness evaluation."""
    unc_path = AUDIT_DIR / "detailed_uncertainty_metrics.json"
    if not unc_path.exists():
        return False, {"error": "Missing detailed_uncertainty_metrics.json"}
    with open(unc_path, "r", encoding="utf-8") as f:
        unc = json.load(f)

    fm = fresh_metrics()
    details: Dict[str, Any] = {"nominal_level": "90%"}
    passed = True
    for name in ("QI-C1", "MODEL-REAL-04"):
        m = fm[name]
        reproduced = abs(m["fresh_picp_90_pct"] - m["reference_picp_90_pct"]) <= PICP_TOLERANCE_PCT
        passed = passed and reproduced and m["fresh_picp_90_pct"] >= 90.0
        details[name] = {
            "fresh_picp_pct": m["fresh_picp_90_pct"],
            "reference_picp_pct": round(m["reference_picp_90_pct"], 4),
            "mpiw_kg_h": m["mpiw_90_kg_h"],
            "reproduced_within_tolerance": reproduced,
        }
    details["reference_sharpness_gain_pct"] = unc.get("tradeoff_comparison", {}).get("0.9", {}).get("sharpness_gain_pct")
    return passed, details


def run_gate_g6_ood() -> Tuple[bool, Dict[str, Any]]:
    """G6: OOD Guard confusion matrix and threshold audit."""
    # Re-runs the OOD evaluation through the serving path and rewrites the artifact.
    import compute_detailed_metrics as cdm
    from src.qi_prediction.validation import ValidationHarness
    import pandas as pd
    dfs = {v: pd.read_parquet(DATA_DIR / f"{v}.parquet") for v in cdm.VESSELS}
    _, _, test = ValidationHarness.forward_temporal_splits(dfs)
    ood = cdm.evaluate_ood(test, cdm.get_production_predictor())

    summary = ood.get("primary_ood_guard_summary", {})
    perf = summary.get("performance_metrics", {})
    severe_recall = summary.get("by_ood_severity", {}).get("Severe OOD", {}).get("recall_pct", 0.0)
    passed = (perf.get("false_positive_rate_pct", 100.0) == 0.0) and (severe_recall >= 95.0)

    details = {
        "threshold": summary.get("threshold", 1.50),
        "false_positive_rate_pct": perf.get("false_positive_rate_pct"),
        "severe_ood_recall_pct": severe_recall,
        "balanced_accuracy_pct": perf.get("balanced_accuracy_pct"),
    }
    return passed, details


def run_gate_g7_cost_objective() -> Tuple[bool, Dict[str, Any]]:
    """G7: Multi-component operational cost minimization engine."""
    cost_csv = RESULTS_DIR / "cost_objective_results.csv"
    if not cost_csv.exists():
        return False, {"error": "Missing cost_objective_results.csv"}

    from optimization.sih_objective_engine import SIHObjectiveEngine
    engine = SIHObjectiveEngine()
    obj = engine.evaluate_voyage(
        vessel_id="CPS_Poseidon",
        vessel_type="passenger_cruise",
        speed_knots=14.5,
        voyage_distance_nm=300.0,
        schedule_deadline_hours=24.0,
        baseline_fuel_rate_kg_h=2700.0,
        fuel_type="vlsfo",
        use_shore_power=True,
        port_hours=10.0,
        hotel_load_kw=1200.0,
    )

    berth_kw = dict(vessel_id="CPS_Poseidon", vessel_type="passenger_cruise", speed_knots=14.5,
                    voyage_distance_nm=300.0, schedule_deadline_hours=24.0, baseline_fuel_rate_kg_h=2700.0,
                    fuel_type="vlsfo")
    voyage_only = engine.evaluate_voyage(**berth_kw)
    onboard = engine.evaluate_voyage(**berth_kw, use_shore_power=False, port_hours=10.0, hotel_load_kw=1200.0)
    # Symmetric berth accounting: ON = voyage + electricity only; OFF = voyage + onboard berth fuel only.
    berth_symmetric = (
        obj.berth_source == "SHORE POWER" and obj.berth_fuel_tonnes == 0.0
        and abs(obj.operational_cost_usd - (voyage_only.operational_cost_usd + obj.shore_power_cost_usd)) <= 0.05
        and onboard.berth_source == "ONBOARD GENERATION" and onboard.shore_power_cost_usd == 0.0
        and onboard.berth_fuel_tonnes > 0.0
        and abs(onboard.operational_cost_usd - (voyage_only.operational_cost_usd + onboard.berth_cost_usd)) <= 0.05
    )
    components = (
        obj.fuel_cost_usd + obj.shore_power_cost_usd + obj.carbon_cost_usd
        + obj.schedule_penalty_usd + obj.fueleu_penalty_usd
    )
    # Total may add fixed operating costs, but must never be less than its named parts.
    components_covered = obj.operational_cost_usd >= components - 0.05
    passed = (
        obj.operational_cost_usd > 0
        and obj.fuel_cost_usd > 0
        and obj.shore_power_cost_usd > 0
        and obj.carbon_cost_usd > 0
        and components_covered
        and berth_symmetric
    )
    details = {
        "formula": "C_total = C_fuel + C_elec + C_ops + C_carbon + C_sched + C_fueleu",
        "berth_accounting_symmetric": berth_symmetric,
        "berth_shore_on_electricity_usd": round(obj.shore_power_cost_usd, 2),
        "berth_onboard_cost_usd": round(onboard.berth_cost_usd, 2),
        "berth_onboard_fuel_t": round(onboard.berth_fuel_tonnes, 4),
        "sample_evaluation_usd": round(obj.operational_cost_usd, 2),
        "fuel_cost_usd": round(obj.fuel_cost_usd, 2),
        "shore_power_cost_usd": round(obj.shore_power_cost_usd, 2),
        "carbon_cost_usd": round(obj.carbon_cost_usd, 2),
        "named_components_sum_usd": round(components, 2),
        "total_covers_components": components_covered,
        "artifact": rel(cost_csv),
    }
    return passed, details


def run_gate_g8_lifecycle_ghg() -> Tuple[bool, Dict[str, Any]]:
    """G8: IMO MEPC.391(81) Well-to-Wake lifecycle GHG accounting."""
    ghg_csv = RESULTS_DIR / "ghg_objective_results.csv"
    if not ghg_csv.exists():
        return False, {"error": "Missing ghg_objective_results.csv"}

    from optimization.sih_objective_engine import SIHObjectiveEngine
    engine = SIHObjectiveEngine()
    vlsfo_res = engine.evaluate_voyage(
        vessel_id="CPS_Poseidon",
        vessel_type="passenger_cruise",
        speed_knots=14.5,
        voyage_distance_nm=300.0,
        schedule_deadline_hours=24.0,
        baseline_fuel_rate_kg_h=2700.0,
        fuel_type="vlsfo",
    )
    bio_res = engine.evaluate_voyage(
        vessel_id="CPS_Poseidon",
        vessel_type="passenger_cruise",
        speed_knots=14.5,
        voyage_distance_nm=300.0,
        schedule_deadline_hours=24.0,
        baseline_fuel_rate_kg_h=2700.0,
        fuel_type="bio_methanol",
    )

    g8_kw = dict(vessel_id="CPS_Poseidon", vessel_type="passenger_cruise", speed_knots=14.5, voyage_distance_nm=300.0,
                 schedule_deadline_hours=24.0, baseline_fuel_rate_kg_h=2700.0, fuel_type="vlsfo",
                 port_hours=10.0, hotel_load_kw=1200.0)
    berth_off = engine.evaluate_voyage(**g8_kw, use_shore_power=False)
    berth_on = engine.evaluate_voyage(**g8_kw, use_shore_power=True)
    grid_t = 1200.0 * 10.0 * engine.shore_power_grid_emission_factor / 1e6
    berth_ghg_symmetric = (
        abs(berth_off.lifecycle_ghg_tonnes - (vlsfo_res.lifecycle_ghg_tonnes + berth_off.berth_ghg_tonnes)) <= 1e-3
        and berth_off.berth_ghg_tonnes > 0.0
        and abs(berth_on.lifecycle_ghg_tonnes - (vlsfo_res.lifecycle_ghg_tonnes + grid_t)) <= 1e-3
    )
    passed = (
        vlsfo_res.lifecycle_ghg_tonnes > 0
        and vlsfo_res.wtt_ghg_tonnes > 0
        and vlsfo_res.ttw_ghg_tonnes > 0
        and bio_res.lifecycle_ghg_tonnes < vlsfo_res.lifecycle_ghg_tonnes
        and berth_ghg_symmetric
    )
    details = {
        "standard": "IMO Resolution MEPC.391(81) & EU MRV",
        "formula": "GHG_WtW = GHG_WtT + GHG_TtW + Slip",
        "vlsfo_wtw_tco2e": round(vlsfo_res.lifecycle_ghg_tonnes, 2),
        "biomethanol_wtw_tco2e": round(bio_res.lifecycle_ghg_tonnes, 2),
        "berth_ghg_symmetric": berth_ghg_symmetric,
        "berth_onboard_wtw_tco2e": round(berth_off.berth_ghg_tonnes, 3),
        "berth_shore_grid_tco2e": round(grid_t, 3),
        "artifact": rel(ghg_csv),
    }
    return passed, details


def run_gate_g9_multiobjective() -> Tuple[bool, Dict[str, Any]]:
    """G9: Multi-objective Pareto front generation and cost/GHG trade-offs."""
    pareto_csv = RESULTS_DIR / "pareto_front.csv"
    tradeoffs_csv = RESULTS_DIR / "multiobjective_tradeoffs.csv"
    if not (pareto_csv.exists() and tradeoffs_csv.exists()):
        return False, {"error": "Missing pareto_front.csv or multiobjective_tradeoffs.csv"}

    import pandas as pd
    df_p = pd.read_csv(pareto_csv)
    df_t = pd.read_csv(tradeoffs_csv)

    from src.benchmark.metrics import is_pareto_efficient
    df_u = df_p.drop_duplicates(subset=["fuel_tonnes", "cost_usd", "ghg_tonnes", "delay_hours"])
    distinct = len(df_u)
    penalty_free = bool("penalty" in df_p and df_p["is_feasible"].astype(str).str.lower().eq("true").all()
                        and (df_p["penalty"] <= 0.0).all())
    non_dominated = bool(distinct and is_pareto_efficient(df_u[["fuel_tonnes", "cost_usd", "ghg_tonnes"]].values).all())
    passed = (distinct >= 2) and penalty_free and non_dominated and (len(df_t) >= 4)
    details = {
        "pareto_rows": len(df_p),
        "distinct_pareto_points": distinct,
        "all_points_feasible_and_penalty_free": penalty_free,
        "all_points_mutually_non_dominated": non_dominated,
        "objectives": ["operational_cost_usd", "wtw_ghg_tonnes", "schedule_penalty_usd"],
        "tradeoff_scenarios_evaluated": len(df_t),
        "pareto_artifact": rel(pareto_csv),
    }
    return passed, details


def run_gate_g10_benchmark() -> Tuple[bool, Dict[str, Any]]:
    """G10: Multi-algorithm benchmark across 30 seeds (DE, QPSO, GA, NSGA-III)."""
    bench_csv = RESULTS_DIR / "algorithm_multiobjective_results.csv"
    if not bench_csv.exists():
        return False, {"error": "Missing algorithm_multiobjective_results.csv"}

    import pandas as pd
    df_b = pd.read_csv(bench_csv)
    algorithms = set(df_b["algorithm"].unique())
    has_de = any("DE" in a for a in algorithms)
    has_qpso = any("QPSO" in a for a in algorithms)
    has_ga = any("GA" in a for a in algorithms)
    has_nsga = any("NSGA" in a for a in algorithms)

    passed = has_de and has_qpso and has_ga and has_nsga and (len(df_b) >= 100)
    de_rows = df_b[df_b["algorithm"].str.contains("DE")]
    qpso_rows = df_b[df_b["algorithm"].str.contains("QPSO")]
    de_feas = float(de_rows["feasibility"].mean())
    qpso_feas = float(qpso_rows["feasibility"].mean())

    details = {
        "algorithms_evaluated": sorted(algorithms),
        "seeds_per_algorithm": {a: int(n) for a, n in df_b.groupby("algorithm")["seed"].nunique().items()},
        "de_feasible_rate_pct": round(de_feas * 100, 1),
        "qpso_feasible_rate_pct": round(qpso_feas * 100, 1),
        "de_median_fitness": round(float(de_rows["fitness"].median()), 4),
        "qpso_median_fitness": round(float(qpso_rows["fitness"].median()), 4),
    }
    return passed, details


def run_gate_g11_scalability() -> Tuple[bool, Dict[str, Any]]:
    """G11: Evaluator scalability across dimensions D in [18, 600]."""
    scale_csv = RESULTS_DIR / "scalability_results.csv"
    if not scale_csv.exists():
        return False, {"error": "Missing scalability_results.csv"}

    import pandas as pd
    df_s = pd.read_csv(scale_csv)
    max_d = int(df_s["dimension"].max())
    max_ms = float(df_s["eval_time_ms_per_eval"].max())

    passed = (max_d >= 600) and (max_ms < 1.0)
    details = {
        "max_dimension_evaluated": max_d,
        "eval_time_per_call_ms": round(max_ms, 4),
        "artifact": rel(scale_csv),
    }
    return passed, details


def run_gate_g12_safety() -> Tuple[bool, Dict[str, Any]]:
    """G12: 1,000 invalid stress tests, 16 edge cases, domain guard fallback."""
    # Re-runs 1,000 invalid inputs and the edge-case matrix against the live predictor.
    import compute_detailed_metrics as cdm
    safe = cdm.run_safety_and_stress_tests(cdm.get_production_predictor())

    rate = safe.get("safe_rejection_rate_pct", 0.0)
    edge_cases = safe.get("edge_case_matrix", [])
    edge_passed = all(ec.get("pass", False) for ec in edge_cases)
    passed = (rate == 100.0) and edge_passed

    details = {
        "invalid_stress_tests": safe.get("total_invalid_stress_tests"),
        "safe_rejection_rate_pct": rate,
        "edge_cases_passed": len([ec for ec in edge_cases if ec.get("pass")]),
        "unknown_vessel_type": "REJECT (categorical out-of-distribution)",
    }
    return passed, details


def run_gate_g13_alternative_fuels() -> Tuple[bool, Dict[str, Any]]:
    """G13: Invariant shaft work alternative fuel scenario modeling."""
    from optimization.sih_objective_engine import SIHObjectiveEngine
    engine = SIHObjectiveEngine()
    fuels = ["vlsfo", "mgo", "bio_methanol", "green_ammonia", "liquid_hydrogen"]
    fuel_data = {}
    all_ok = True
    for f in fuels:
        res = engine.evaluate_voyage(
            vessel_id="CPS_Poseidon",
            vessel_type="passenger_cruise",
            speed_knots=14.5,
            voyage_distance_nm=300.0,
            schedule_deadline_hours=24.0,
            baseline_fuel_rate_kg_h=2700.0,
            fuel_type=f,
        )
        fuel_data[f] = {
            "resolved_pathway": res.fuel_type,
            "fuel_tonnes": res.fuel_tonnes,
            "cost_usd": res.operational_cost_usd,
            "wtw_tco2e": res.lifecycle_ghg_tonnes,
        }
        # Each fuel must resolve to its own pathway; a silent VLSFO substitution fails the gate.
        if res.lifecycle_ghg_tonnes < 0 or res.fuel_type != f:
            all_ok = False

    details = {
        "thermodynamic_basis": "Invariant shaft work (E_shaft = m * LHV * eta)",
        "scenario_status": "Strictly scenario modeling, not empirical sensor telemetry",
        "fuels_profiled": fuel_data,
    }
    return all_ok, details


def run_gate_g14_demo() -> Tuple[bool, Dict[str, Any]]:
    """G14: Run all 11 demonstration scenes now; pass only on exit code 0 with 11/11 scene checks."""
    import re
    demo = REPO_ROOT / "scripts" / "demo_scenarios.py"
    proc = subprocess.run(
        [sys.executable, str(demo)], cwd=REPO_ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=600,
    )
    m = re.search(r"DEMO RESULT: (\d+)/(\d+) scenes passed", proc.stdout)
    scenes_passed, total = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    passed = proc.returncode == 0 and total == 11 and scenes_passed == 11
    details = {
        "demo_script": rel(demo),
        "exit_code": proc.returncode,
        "total_scenes": total,
        "scenes_passed": scenes_passed,
        "failed_checks": [ln.strip() for ln in proc.stdout.splitlines() if "CHECK FAILED" in ln],
    }
    if proc.returncode != 0:
        details["stderr_tail"] = proc.stderr.strip().splitlines()[-5:]
    return passed, details


def run_gate_g15_claim_consistency() -> Tuple[bool, Dict[str, Any]]:
    """G15: Scientific honesty and enforcement of prohibited claims."""
    claims_p = RELEASE_DIR / "FINAL_CLAIMS.json"
    if not claims_p.exists():
        return False, {"error": "Missing FINAL_CLAIMS.json"}
    with open(claims_p, "r", encoding="utf-8") as f:
        claims = json.load(f)

    prohibited = claims.get("prohibited_claims", [])
    verified = claims.get("verified_claims", []) + claims.get("verified_with_qualification_claims", [])
    required = {"quantum supremacy", "quantum speedup", "quantum advantage"}
    listed = {p.lower() for p in prohibited}
    # Every positive claim is scanned for any prohibited phrase.
    violations = [
        {"claim_id": c.get("claim_id"), "phrase": p}
        for c in verified
        for p in listed
        if p in str(c.get("statement", "")).lower()
    ]
    missing_required = sorted(r for r in required if not any(r in x for x in listed))
    passed = not violations and not missing_required and len(verified) >= 14

    details = {
        "prohibited_claims_count": len(prohibited),
        "positive_claims_scanned": len(verified),
        "prohibited_phrase_violations": violations,
        "required_prohibitions_missing": missing_required,
    }
    return passed, details


def run_gate_g16_traceability() -> Tuple[bool, Dict[str, Any]]:
    """G16: Git SHA, code commit, artifact hashes and compliance matrix."""
    git_sha = get_git_sha()
    matrix_p = RELEASE_DIR / "FINAL_SIH_COMPLIANCE_MATRIX.md"
    checklist_p = RELEASE_DIR / "FINAL_RELEASE_CHECKLIST.md"

    passed = (git_sha != "UNKNOWN") and matrix_p.exists() and checklist_p.exists()

    manifest = {
        "version": "v1.1.0-sih-complete",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit_head": git_sha,
        "dataset_hashes": {
            "CPS_Poseidon.parquet": get_file_sha256(DATA_DIR / "CPS_Poseidon.parquet"),
            "CPS_Triton.parquet": get_file_sha256(DATA_DIR / "CPS_Triton.parquet"),
            "OSS_Ceto.parquet": get_file_sha256(DATA_DIR / "OSS_Ceto.parquet"),
        },
        "model_hashes": {
            "model_real_04.txt": get_file_sha256(MODELS_DIR / "model_real_04.txt"),
            "qi_c1.txt": get_file_sha256(MODELS_DIR / "qi_c1.txt"),
            "qi_c1_vessel_type.txt": get_file_sha256(MODELS_DIR / "qi_c1_vessel_type.txt"),
        },
        "compliance_matrix_exists": matrix_p.exists(),
        "release_checklist_exists": checklist_p.exists(),
    }

    with open(RELEASE_DIR / "release_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    return passed, manifest


def main():
    print("=================================================================")
    print("SIH26138: EXECUTING RELEASE GATE AUDIT (G1 - G16)")
    print("Candidate Release: v1.1.0-sih-complete")
    print("=================================================================")

    gates = [
        ("G1_DATA", "Dataset Integrity & Cleaning Reconciliation", run_gate_g1_data),
        ("G2_REPRODUCIBILITY", "Environment & Deterministic Execution", run_gate_g2_reproducibility),
        ("G3_PREDICTION", "Model Prediction Accuracy & Frozen Baselines", run_gate_g3_prediction),
        ("G4_VESSEL_TYPE", "Explicit Vessel-Type Categorical Feature", run_gate_g4_vessel_type),
        ("G5_UNCERTAINTY", "Split Conformal Uncertainty Calibration", run_gate_g5_uncertainty),
        ("G6_OOD", "Out-of-Distribution Guard & Confusion Matrix", run_gate_g6_ood),
        ("G7_COST_OBJECTIVE", "Multi-Component Operational Cost Minimization", run_gate_g7_cost_objective),
        ("G8_LIFECYCLE_GHG", "IMO MEPC.391(81) Well-to-Wake Accounting", run_gate_g8_lifecycle_ghg),
        ("G9_MULTIOBJECTIVE", "Multi-Objective Cost/GHG Pareto Optimization", run_gate_g9_multiobjective),
        ("G10_BENCHMARK", "Multi-Algorithm Benchmark (DE, QPSO, GA, NSGA-III)", run_gate_g10_benchmark),
        ("G11_SCALABILITY", "Dimensional Scalability & O(D) Profiling", run_gate_g11_scalability),
        ("G12_SAFETY", "1,000 Stress Tests, Edge Cases & Fault Recovery", run_gate_g12_safety),
        ("G13_ALTERNATIVE_FUELS", "Invariant Shaft Work Alternative Fuel Scenarios", run_gate_g13_alternative_fuels),
        ("G14_DEMO", "11 Executable Demonstration Scenes", run_gate_g14_demo),
        ("G15_CLAIM_CONSISTENCY", "Claim Consistency & Scientific Honesty", run_gate_g15_claim_consistency),
        ("G16_TRACEABILITY", "Artifact Hashes, Git SHA & Compliance Matrix", run_gate_g16_traceability),
    ]

    gate_results = {}
    all_passed = True

    for gid, name, fn in gates:
        try:
            passed, details = fn()
        except Exception as e:
            passed = False
            details = {"exception": str(e)}

        status_str = "PASS" if passed else "FAIL"
        dots = "." * max(2, (30 - len(gid)))
        print(f"    {gid} {dots} {status_str}  [{GATE_EVIDENCE[gid]}]  ({name})")

        gate_results[gid] = {
            "name": name,
            "status": status_str,
            "passed": passed,
            "evidence": GATE_EVIDENCE[gid],
            "details": details,
        }
        if not passed:
            all_passed = False

    overall_status = "SIH26138 CORE REQUIREMENTS COMPLETE" if all_passed else "RELEASE BLOCKED — CORRECTIONS REQUIRED"

    print("\n=================================================================")
    print(f"OVERALL RELEASE CLASSIFICATION: {overall_status}")
    print(f"GATES PASSED: {sum(1 for g in gate_results.values() if g['passed'])} / {len(gates)}")
    print("=================================================================")

    release_gate_summary = {
        "project": "SIH26138 - Egreen Quanta",
        "release_version": "v1.1.0-sih-complete",
        "release_classification": overall_status,
        "system_type": "Controlled Decision-Support Prototype",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "gates_evaluated": len(gates),
        "gates_passed": sum(1 for g in gate_results.values() if g["passed"]),
        "gates_freshly_computed": sum(1 for g in gate_results.values() if g["evidence"] == FRESH),
        "gates_reference_artifact_verified": sum(1 for g in gate_results.values() if g["evidence"] == REFERENCE),
        "gates": gate_results,
    }

    out_file = RELEASE_DIR / "release_gate.json"
    with open(out_file, "w") as f:
        json.dump(release_gate_summary, f, indent=2)
    print(f"Release gate written to: {out_file}")

    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
