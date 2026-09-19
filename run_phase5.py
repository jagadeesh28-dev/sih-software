"""
Master Execution Script for Phase 5 of SIH26138 (Egreen Quanta).
Runs the complete benchmark suite, statistical testing, validation benchmarks,
and publication figure generation in a single reproducible command.
"""

import sys
import time
from pathlib import Path

ROOT_DIR = Path(".").resolve()
sys.path.insert(0, str(ROOT_DIR))

from common.logger import setup_logger
from src.benchmark.runner import execute_phase5_master_benchmark
from src.visualization.plots import generate_all_phase5_figures

logger = setup_logger("run_phase5_master")


def main():
    t_start = time.perf_counter()
    logger.info("=" * 80)
    logger.info("STARTING PHASE 5 MASTER BENCHMARK PIPELINE")
    logger.info("Heterogeneous Quantum-Inspired Fleet Optimization (A0-A5 Ablation + Panel)")
    logger.info("=" * 80)

    phase5_dir = ROOT_DIR / "PHASE5"
    phase5_dir.mkdir(parents=True, exist_ok=True)

    # 1. Run Master Benchmark
    benchmark_data = execute_phase5_master_benchmark(output_root=phase5_dir)

    # 2. Generate all 18 mandatory figures
    logger.info("Generating all 18 publication-quality figures into PHASE5/figures/...")
    fig_dir = phase5_dir / "figures"
    generate_all_phase5_figures(benchmark_data, fig_dir=fig_dir)

    t_end = time.perf_counter()
    elapsed_min = (t_end - t_start) / 60.0
    logger.info("=" * 80)
    logger.info(f"PHASE 5 MASTER BENCHMARK PIPELINE COMPLETE in {elapsed_min:.2f} minutes.")
    logger.info(f"All CSV artifacts written to: {phase5_dir / 'results'}")
    logger.info(f"All validation artifacts written to: {phase5_dir / 'validation'}")
    logger.info(f"All figure artifacts written to: {fig_dir}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
