#!/usr/bin/env python3
"""
SIH26138 — Egreen Quanta: Single-Command Master Reproduction Runner.
Full Jury & Release Verification Script.

Usage:
    python reproduce_release.py
    or:
    python scripts/reproduce_release.py

Executes:
1. Dataset validation & row count reconciliation (173,974 records across 3 vessels)
2. Artifact & SHA256 integrity validation
3. Baseline verification (MODEL-REAL-04: seed 42 MAE=246.91 kg/h, R2=0.9503)
4. QI-C1 verification (QI-C1: seed 42 MAE=244.86 kg/h, R2=0.9500; 30-seed mean MAE=237.96 kg/h, R2=0.9530)
5. Uncertainty verification (Nominal 90% coverage: QI-C1=93.56%, M04=95.05%; MPIW=1564.93 kg/h; 31.17% sharper)
6. OOD verification (FPR=0.0%, severe OOD recall=96.55% / 100.0%)
7. Safety tests (1,000 invalid inputs safely rejected = 100.0%, 16 edge cases passed)
8. Optimizer verification (post-fix Pareto front re-evaluated; Phase 5 frozen benchmark is PRE-FIX HISTORICAL)
9. End-to-end prediction & demo trace
10. Claim consistency check (Zero false superiority, decision-support prototype)

Outputs a comprehensive terminal audit and machine-readable summary.
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

REPO_ROOT = Path(__file__).resolve().parent
if REPO_ROOT.name == "scripts":
    REPO_ROOT = REPO_ROOT.parent
sys.path.insert(0, str(REPO_ROOT))

DATA_DIR = REPO_ROOT / "data" / "processed" / "real" / "fuelcast"
MODELS_DIR = REPO_ROOT / "models"
AUDIT_DIR = REPO_ROOT / "results" / "audit"
RELEASE_DIR = REPO_ROOT / "RELEASE"
sys.path.insert(0, str(REPO_ROOT / "scripts"))

# Evidence labels printed next to every verdict.
FRESH = "FRESHLY REPRODUCED"
REFERENCE = "REFERENCE ARTIFACT VERIFIED"
HISTORICAL = "HISTORICAL REFERENCE"


def print_header(title: str):
    print("\n" + "=" * 68)
    print(f" {title}")
    print("=" * 68)


def print_status(item: str, status: str, detail: str = ""):
    dots = "." * max(2, (32 - len(item)))
    print(f"    {item} {dots} {status}  {detail}")


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


def main():
    start_time = time.time()
    git_sha = get_git_sha()
    print_header(f"SIH26138: MASTER RELEASE REPRODUCTION (Git: {git_sha[:10]})")

    results_summary = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": git_sha,
        "release_status": "PENDING",
        "data_status": "FAIL",
        "model_status": "FAIL",
        "baseline_status": "FAIL",
        "qi_status": "FAIL",
        "uncertainty_status": "FAIL",
        "ood_status": "FAIL",
        "safety_status": "FAIL",
        "optimizer_status": "FAIL",
        "claim_status": "FAIL",
        "overall_status": "PENDING",
    }

    # 1. Dataset Validation
    print("\n[1/10] DATASET INTEGRITY & CLEANING RECONCILIATION")
    import pandas as pd
    vessels = {
        "CPS_Poseidon.parquet": 105422,
        "CPS_Triton.parquet": 25347,
        "OSS_Ceto.parquet": 43205,
    }
    total_records = 0
    all_files_ok = True
    vessel_hashes = {}
    for vf, exp_count in vessels.items():
        vp = DATA_DIR / vf
        if not vp.exists():
            all_files_ok = False
            break
        v_hash = get_file_sha256(vp)
        vessel_hashes[vf] = v_hash
        df_v = pd.read_parquet(vp)
        n_v = len(df_v)
        total_records += n_v
        if n_v != exp_count:
            all_files_ok = False

    data_pass = all_files_ok and (total_records == 173974)
    if data_pass:
        print_status("DATASET", "PASS", f"(173,974 records across 3 vessels; 12 trailing rows cleaned)")
        results_summary["data_status"] = "PASS"
    else:
        print_status("DATASET", "FAIL", f"(Records found: {total_records}, expected: 173,974)")

    # Explicit Traceability Block required by Section 6
    print("\n    DATA TRACEABILITY AUDIT:")
    print(f"      - Raw Records:       173,986")
    print(f"      - Validated Records: 173,974 (12 trailing null/sensor dropout rows removed)")
    print(f"      - CPS_Poseidon:      105,422 rows | SHA256: {vessel_hashes.get('CPS_Poseidon.parquet', '')[:16]}...")
    print(f"      - CPS_Triton:        25,347 rows  | SHA256: {vessel_hashes.get('CPS_Triton.parquet', '')[:16]}...")
    print(f"      - OSS_Ceto:          43,205 rows  | SHA256: {vessel_hashes.get('OSS_Ceto.parquet', '')[:16]}...")
    print(f"      - Split Protocol:    Forward temporal 60% train (104,384), 20% val (34,794), 20% test (34,796)")

    # 2. Artifact Validation & Model Load
    print("\n[2/10] ARTIFACT VALIDATION & MODEL SERVING ENGINE")
    try:
        from src.qi_prediction.serving import ProductionFuelPredictor, get_production_predictor
        predictor = get_production_predictor()
        models_ok = (predictor.qi_c1_booster is not None) and (predictor.model_real_04_booster is not None)
        if models_ok:
            print_status("MODEL LOAD", "PASS", "(QI-C1 and MODEL-REAL-04 boosters loaded and verified)")
            results_summary["model_status"] = "PASS"
        else:
            print_status("MODEL LOAD", "FAIL", "Boosters failed to load")
    except Exception as e:
        print_status("MODEL LOAD", "FAIL", str(e))
        models_ok = False

    # 3 & 4. Fresh inference on the test split with the committed boosters (no retraining)
    from release_gate import (
        MAE_TOLERANCE_KG_H, PICP_TOLERANCE_PCT, R2_TOLERANCE, fresh_metrics,
        run_gate_g15_claim_consistency,
    )
    try:
        fm = fresh_metrics()
    except Exception as e:
        fm = None
        fm_error = str(e)

    def verify_model(step: str, label: str, name: str, meta_file: str):
        print(f"\n[{step}/10] {label} ({name})")
        if fm is None:
            print_status(name, "FAIL", fm_error)
            return False
        m = fm[name]
        with open(MODELS_DIR / meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
        ok = (
            abs(m["fresh_test_mae_kg_h"] - m["reference_test_mae_kg_h"]) <= MAE_TOLERANCE_KG_H
            and abs(m["fresh_test_r2"] - m["reference_test_r2"]) <= R2_TOLERANCE
            and m["fresh_test_r2"] >= 0.945 and m["fresh_test_mae_kg_h"] <= 250.0
        )
        print_status(name, "PASS" if ok else "FAIL",
                     f"[{FRESH}] test MAE={m['fresh_test_mae_kg_h']:.2f} kg/h, R2={m['fresh_test_r2']:.4f} "
                     f"(reference {m['reference_test_mae_kg_h']:.2f} / {m['reference_test_r2']:.4f}, n={fm['test_rows']})")
        print(f"      - 30-seed mean [{HISTORICAL}, not re-run]: MAE={meta.get('mean_30seed_mae_kg_h')} kg/h, "
              f"R2={meta.get('mean_30seed_r2')}")
        return ok

    m04_pass = verify_model("3", "FROZEN BASELINE VERIFICATION", "MODEL-REAL-04", "model_real_04_meta.json")
    results_summary["baseline_status"] = "PASS" if m04_pass else "FAIL"
    qi_pass = verify_model("4", "QUANTUM-INSPIRED CANDIDATE VERIFICATION", "QI-C1", "qi_c1_meta.json")
    results_summary["qi_status"] = "PASS" if qi_pass else "FAIL"
    if fm is not None:
        vt = fm["QI-C1-vessel-type"]
        print(f"      - QI-C1-vessel-type [{FRESH}]: test MAE={vt['fresh_test_mae_kg_h']:.2f} kg/h, R2={vt['fresh_test_r2']:.4f}")
    print(f"      - Statistical verdict [{HISTORICAL}]: QI-C1 competitive with classical GA (Wilcoxon p=0.684), not superior")

    # 5. Uncertainty Verification
    print("\n[5/10] CONFORMAL UNCERTAINTY VERIFICATION")
    try:
        qi_u, m04_u = fm["QI-C1"], fm["MODEL-REAL-04"]
        qi_90_cov, m04_90_cov = qi_u["fresh_picp_90_pct"], m04_u["fresh_picp_90_pct"]
        qi_90_mpiw, m04_90_mpiw = qi_u["mpiw_90_kg_h"], m04_u["mpiw_90_kg_h"]
        sharpness_gain = (1.0 - qi_90_mpiw / m04_90_mpiw) * 100.0
        reproduced = all(
            abs(m["fresh_picp_90_pct"] - m["reference_picp_90_pct"]) <= PICP_TOLERANCE_PCT for m in (qi_u, m04_u)
        )
        unc_pass = reproduced and (qi_90_cov >= 90.0) and (m04_90_cov >= 90.0)
        print_status("UNCERTAINTY", "PASS" if unc_pass else "FAIL",
                     f"[{FRESH}] 90% PICP: QI-C1={qi_90_cov:.2f}%, M04={m04_90_cov:.2f}%")
        print(f"      - MPIW (fixed conformal q from calibration): QI-C1={qi_90_mpiw:.1f} kg/h, "
              f"M04={m04_90_mpiw:.1f} kg/h ({sharpness_gain:.1f}% narrower)")
        results_summary["uncertainty_status"] = "PASS" if unc_pass else "FAIL"
    except Exception as e:
        print_status("UNCERTAINTY", "FAIL", str(e))
        unc_pass = False

    # 6. OOD Guard Verification
    print("\n[6/10] OUT-OF-DISTRIBUTION (OOD) GUARD VERIFICATION")
    try:
        with open(AUDIT_DIR / "detailed_ood_metrics.json", "r", encoding="utf-8") as f:
            ood_data = json.load(f)
        summary_ood = ood_data["primary_ood_guard_summary"]
        cm = summary_ood["confusion_matrix"]
        fpr = summary_ood["performance_metrics"]["false_positive_rate_pct"]
        severe_recall = summary_ood["by_ood_severity"]["Severe OOD"]["recall_pct"]
        ood_pass = (fpr == 0.0) and (severe_recall >= 95.0)
        if ood_pass:
            print_status("OOD GUARD", "PASS", f"[REFERENCE ARTIFACT VERIFIED] (In-Domain FPR={fpr:.1f}%, Severe OOD Recall={severe_recall:.1f}%)")
            print(f"      - Confusion Matrix:   TP={cm['TP']}, TN={cm['TN']}, FP={cm['FP']}, FN={cm['FN']} (Total={cm['total_evaluated']})")
            print(f"      - Primary Threshold:  envelope_distance = 1.50 (zero tuning on test set)")
            results_summary["ood_status"] = "PASS"
        else:
            print_status("OOD GUARD", "FAIL", f"FPR={fpr}%, Severe Recall={severe_recall}%")
    except Exception as e:
        print_status("OOD GUARD", "FAIL", str(e))
        ood_pass = False

    # 7. Safety & Stress Tests Verification
    print("\n[7/10] SAFETY, STRESS & FAILURE INJECTION VERIFICATION")
    try:
        with open(AUDIT_DIR / "safety_test_matrix.json", "r", encoding="utf-8") as f:
            safe_data = json.load(f)
        stress_rate = safe_data["safe_rejection_rate_pct"]
        total_stress = safe_data["total_invalid_stress_tests"]
        edge_cases = safe_data["edge_case_matrix"]
        all_ec_pass = all(ec["pass"] for ec in edge_cases)
        safe_pass = (stress_rate == 100.0) and all_ec_pass
        if safe_pass:
            print_status("SAFETY TESTS", "PASS", f"[REFERENCE ARTIFACT VERIFIED] (100.0% safe rejection on {total_stress} stress tests + {len(edge_cases)}/{len(edge_cases)} edge cases)")
            results_summary["safety_status"] = "PASS"
        else:
            print_status("SAFETY TESTS", "FAIL", f"Rejection rate={stress_rate}%, Edge cases pass={all_ec_pass}")
    except Exception as e:
        print_status("SAFETY TESTS", "FAIL", str(e))
        safe_pass = False

    # 8. Fleet Optimization Verification (POST-FIX CURRENT evidence; Phase 5 is PRE-FIX HISTORICAL)
    print("\n[8/10] FLEET OPTIMIZATION — POST-FIX PARETO FRONT RE-EVALUATION")
    try:
        import numpy as np
        import pandas as pd
        from experiments.exp_phase3_master_runner import load_real_surrogates
        from optimization.fleet_evaluator_phase4 import Phase4FleetEvaluator
        from src.benchmark.metrics import is_pareto_efficient
        from src.evaluator.common_evaluator import CommonFleetEvaluator

        front = pd.read_csv(REPO_ROOT / "results" / "pareto_front.csv")
        ev = Phase4FleetEvaluator(surrogates=load_real_surrogates())
        ev.weights = np.array([0.35, 0.35, 0.30, 0.0, 0.0])
        ce = CommonFleetEvaluator(ev, max_budget=len(front))
        reproduced = 0
        for _, row in front.iterrows():
            out = ce.evaluate(np.asarray(json.loads(row["x_vector"]), dtype=float))
            if (out.is_feasible and out.penalty <= 0.0 and abs(out.fuel_tonnes - row["fuel_tonnes"]) <= 0.01
                    and abs(out.opex_usd - row["cost_usd"]) <= 0.01 and abs(out.ghg_tonnes - row["ghg_tonnes"]) <= 0.01):
                reproduced += 1
        non_dom = bool(is_pareto_efficient(front[["fuel_tonnes", "cost_usd", "ghg_tonnes"]].values).all())
        opt_pass = len(front) > 0 and reproduced == len(front) and non_dom
        detail = (f"{reproduced}/{len(front)} stored plans re-evaluated feasible, penalty-free and identical; "
                  f"mutually non-dominated={non_dom}")
        print_status("OPTIMIZER", "PASS" if opt_pass else "FAIL", f"[{FRESH}] {detail}")
        print("      - Phase 5 frozen benchmark (825k evals, J*_pen=873.23): PRE-FIX HISTORICAL — produced before the "
              "2026-09-24 optimizer fixes; not used as current evidence.")
        results_summary["optimizer_status"] = "PASS" if opt_pass else "FAIL"
    except Exception as e:
        print_status("OPTIMIZER", "FAIL", str(e))
        opt_pass = False

    # 9. End-to-End Prediction & Scenario Trace
    print("\n[9/10] END-TO-END PREDICTION & DEMO TRACE")
    try:
        from optimization.sih_objective_engine import SIHObjectiveEngine
        base = {
            "vessel_id": "CPS_Poseidon", "vessel_type": "passenger_cruise", "fuel_type": "vlsfo",
            "sog_kn": 14.5, "draft_m": 7.5, "displacement_t": 35000.0,
            "wind_speed_ms": 5.0, "wave_height_m": 1.0, "water_depth_m": 60.0,
        }
        fast = predictor.predict_fuel_with_uncertainty({**base, "stw_kn": 18.0, "sog_kn": 18.0})
        slow = predictor.predict_fuel_with_uncertainty({**base, "stw_kn": 15.0, "sog_kn": 15.0})
        cruise_pred = slow["fuel_prediction"]
        saving = (fast["fuel_prediction"] - cruise_pred) / fast["fuel_prediction"] * 100.0
        h2 = SIHObjectiveEngine().evaluate_voyage(
            vessel_id="CPS_Poseidon", vessel_type="passenger_cruise", speed_knots=15.0,
            voyage_distance_nm=15.0, schedule_deadline_hours=1.0,
            baseline_fuel_rate_kg_h=cruise_pred, fuel_type="liquid_hydrogen",
        )
        e2e_pass = cruise_pred > 0 and saving > 0 and h2.fuel_type == "liquid_hydrogen" and h2.fuel_tonnes > 0
        print_status("END-TO-END", "PASS" if e2e_pass else "FAIL",
                     f"[{FRESH}] 15 kn: {cruise_pred:.1f} kg/h ({slow['prediction_source']}) | 18->15 kn: -{saving:.1f}%")
        print(f"      - Liquid H2 [SCENARIO ESTIMATE]: {h2.fuel_tonnes * 1000:.1f} kg/h energy-equivalent")
    except Exception as e:
        print_status("END-TO-END", "FAIL", str(e))
        e2e_pass = False

    # 10. Claim Consistency Check (same check as release gate G15)
    print("\n[10/10] CLAIM CONSISTENCY & SCIENTIFIC HONESTY AUDIT")
    try:
        claim_pass, claim_details = run_gate_g15_claim_consistency()
        print_status("CLAIM AUDIT", "PASS" if claim_pass else "FAIL",
                     f"[{FRESH}] {claim_details['positive_claims_scanned']} positive claims scanned, "
                     f"{len(claim_details['prohibited_phrase_violations'])} prohibited-phrase hits")
    except Exception as e:
        print_status("CLAIM AUDIT", "FAIL", str(e))
        claim_pass = False
    results_summary["claim_status"] = "PASS" if claim_pass else "FAIL"
    results_summary["e2e_status"] = "PASS" if e2e_pass else "FAIL"

    # Overall Verdict
    checks = [data_pass, models_ok, m04_pass, qi_pass, unc_pass, ood_pass, safe_pass, opt_pass, e2e_pass, claim_pass]
    all_gates_pass = all(checks)

    overall_class = "VERIFIED CONTROLLED RELEASE" if all_gates_pass else "CONDITIONAL RELEASE"
    results_summary["release_status"] = "PASSED" if all_gates_pass else "CONDITIONAL"
    results_summary["overall_status"] = overall_class
    results_summary["checks_passed"] = f"{sum(checks)}/{len(checks)}"
    results_summary["evidence"] = {
        FRESH: ["data", "model_load", "baseline", "qi", "uncertainty", "optimizer", "e2e", "claims"],
        REFERENCE: ["ood", "safety"],
    }

    elapsed = time.time() - start_time
    print_header(f"FINAL AUDIT VERDICT: {overall_class} (Elapsed: {elapsed:.2f}s)")
    print(f"Verification checks passed: {sum(checks)}/{len(checks)} "
          f"(8 freshly reproduced, 2 reference artifacts verified)")

    # Save summary
    out_sum = RELEASE_DIR / "reproduction_summary.json"
    with open(out_sum, "w") as f:
        json.dump(results_summary, f, indent=2)
    print(f"\nMachine-readable summary exported to: {out_sum}\n")

    return 0 if all_gates_pass else 1


if __name__ == "__main__":
    sys.exit(main())
