"""
Benchmark harness and statistical evaluation framework.
Enforces equal computational budgets, common random numbers, and paired non-parametric tests.
"""

from .harness import BenchmarkHarness
from .metrics import compute_hypervolume, compute_igd
from .statistics import perform_wilcoxon_test, compute_vargha_delaney_a, classify_outcome

__all__ = [
    "BenchmarkHarness",
    "compute_hypervolume",
    "compute_igd",
    "perform_wilcoxon_test",
    "compute_vargha_delaney_a",
    "classify_outcome",
]
