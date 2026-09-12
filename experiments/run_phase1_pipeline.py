"""
Runner script for Phase 1 Data Pipeline, Quality Audit, Scientific Validation Gate, and QPSO Benchmarks.
Executes all Phase 1 components and populates results directories.
"""

import sys
from pathlib import Path

pkg_root = Path(__file__).resolve().parent.parent
if str(pkg_root) not in sys.path:
    sys.path.insert(0, str(pkg_root))

from common.logger import setup_logger
from common.reproducibility import save_metadata, set_seed
from data.synthetic_generator import generate_synthetic_maritime_dataset
from data.data_quality import DataQualityAuditor
from data.splitting import LeakageSafeSplitter
from scientific_validation.validation_gate import execute_validation_gate
from scientific_validation.qpso_benchmark import benchmark_qpso_mathematical_functions

logger = setup_logger("phase1_pipeline")


def main():
    set_seed(42)
    logger.info("==================================================")
    logger.info("EXECUTING SIH26138 PHASE 1 VALIDATION PIPELINE")
    logger.info("==================================================")

    # 1. Generate Synthetic Dataset
    synth_path = pkg_root / "data" / "synthetic" / "synthetic_vessel_telemetry.csv"
    logger.info(f"Generating synthetic dataset with controlled anomalies at {synth_path}...")
    df = generate_synthetic_maritime_dataset(
        n_records=1200,
        seed=42,
        output_path=synth_path,
        inject_anomalies=True,
    )
    logger.info(f"Generated {len(df)} records across 3 vessels.")

    # 2. Data Quality Audit
    logger.info("Running 16-dimension Data Quality Auditor...")
    auditor = DataQualityAuditor()
    audit_res = auditor.audit_dataset(
        df=df,
        output_dir=pkg_root / "results" / "data_quality",
        nominal_interval_seconds=300.0,
    )
    cls = audit_res["summary"]["classifications"]
    logger.info(
        f"Audit Complete: VALID={cls['VALID']['count']} ({cls['VALID']['percentage']:.1f}%), "
        f"SUSPICIOUS={cls['SUSPICIOUS']['count']} ({cls['SUSPICIOUS']['percentage']:.1f}%), "
        f"INVALID={cls['INVALID']['count']} ({cls['INVALID']['percentage']:.1f}%), "
        f"MISSING={cls['MISSING']['count']} ({cls['MISSING']['percentage']:.1f}%)"
    )

    # 3. Leakage-Safe Splitting Test
    logger.info("Testing Leakage-Safe Data Splitting...")
    # Use only valid records for splitting
    valid_mask = [c == "VALID" for c in audit_res["row_classifications"]]
    df_valid = df[valid_mask].copy()

    splitter = LeakageSafeSplitter(train_ratio=0.70, val_ratio=0.15, test_ratio=0.15)
    train_df, val_df, test_df = splitter.temporal_split(df_valid)
    logger.info(f"Temporal Split: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")

    train_holdout, test_holdout = splitter.leave_vessel_out_split(df_valid, holdout_vessel_id="VESSEL_HM_03")
    logger.info(f"Leave-Vessel-Out: Train={len(train_holdout)} (Vessels {train_holdout['vessel_id'].unique()}), Test={len(test_holdout)} (Vessels {test_holdout['vessel_id'].unique()})")

    # 4. Scientific Validation Gate
    logger.info("Executing Scientific Validation Gate...")
    gate_res = execute_validation_gate(output_dir=pkg_root / "results" / "scientific_validation")
    logger.info(f"Physics Hand-Check Status: {gate_res['physics_validation']['physics_validation_status']}")
    logger.info(f"Smoke Test Reproduction Match: {gate_res['smoke_reproduction']['all_reproduced']}")
    for k, v in gate_res["smoke_reproduction"]["comparison"].items():
        logger.info(f"  {k}: Target={v['target']} vs Recomputed={v['recomputed']:.2f} (Rel Diff={v['rel_difference_pct']:.4f}%)")

    # 5. QPSO Mathematical Benchmark
    logger.info("Executing QPSO Mathematical Function Benchmarks (Sphere, Rastrigin, Rosenbrock)...")
    qpso_res = benchmark_qpso_mathematical_functions(
        dim=5,
        n_particles=40,
        max_iterations=150,
        seed=42,
        output_dir=pkg_root / "results" / "qpso_benchmarks",
    )
    logger.info(f"QPSO Benchmarks Status: {qpso_res['status']}")
    for name, r in qpso_res["benchmarks"].items():
        logger.info(f"  {name.upper()}: Initial={r['initial_score']:.2f} -> Best={r['final_best_score']:.4f} (Reduction={r['score_reduction_pct']:.1f}%)")

    # 6. Save Experiment Metadata
    save_metadata(
        output_path=pkg_root / "results" / "experiments" / "phase1_experiment_metadata.json",
        experiment_id="EXP-PHASE1-PIPELINE",
        seed=42,
        config_snapshot={
            "n_records": len(df),
            "gate_status": gate_res["gate_status"],
            "qpso_status": qpso_res["status"],
        },
    )

    logger.info("==================================================")
    logger.info("PHASE 1 VALIDATION PIPELINE FINISHED SUCCESSFULLY")
    logger.info("==================================================")


if __name__ == "__main__":
    main()
