"""
Benchmark Harness orchestrating multi-algorithm equal-budget comparisons.
Controls independent random seeds, evaluation budgets, and metric aggregation.
"""

from typing import Any, Dict, List, Optional
import numpy as np
from common.logger import get_logger
from common.config_loader import load_config
from .metrics import compute_hypervolume
from .statistics import perform_wilcoxon_test

logger = get_logger(__name__)


class BenchmarkHarness:
    """Orchestrates fair multi-seed benchmarks across QPSO, NSGA-III, and MOEA/D."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or load_config("benchmark.yaml")
        self.budget = self.config["budget"]["evaluation_budget"]
        self.seeds = self.config["budget"]["seeds"]
        self.ref_point = np.array(self.config["metrics"]["hypervolume"]["reference_point"])

    def run_benchmark(self, problem, n_seeds: int = 5) -> Dict[str, Any]:
        """
        Execute benchmark over a subset or all seeds.
        In Phase 0, provides the verified orchestration interface.
        """
        active_seeds = self.seeds[:n_seeds]
        logger.info(f"Running benchmark across {len(active_seeds)} seeds with budget {self.budget}")

        return {
            "evaluation_budget": self.budget,
            "seeds_evaluated": active_seeds,
            "status": "INITIALIZED",
        }
